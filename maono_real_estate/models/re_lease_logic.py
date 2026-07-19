# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ReLease(models.Model):
    _inherit = 're.lease'

    # ----------------------------------------------------------------
    #  WIZARD LAUNCHERS
    # ----------------------------------------------------------------

    def action_renew_lease(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renouveler le bail'),
            'res_model': 're.lease.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lease_id': self.id,
                'default_new_rent_amount': self.rent_amount,
            }
        }

    def action_close_lease(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Résilier le bail'),
            'res_model': 're.lease.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lease_id': self.id}
        }

    def action_compute_penalties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Calculer les pénalités'),
            'res_model': 're.penalty.compute.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lease_id': self.id}
        }

    def action_view_penalties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pénalités'),
            'res_model': 're.penalty',
            'view_mode': 'list,form',
            'domain': [('lease_id', '=', self.id)],
            'context': {'default_lease_id': self.id}
        }

    # ----------------------------------------------------------------
    #  FACTURATION RÉCURRENTE (CRON)
    # ----------------------------------------------------------------

    @api.model
    def _cron_lease_create_quittance(self):
        """Cron quotidien : Génère les quittances pour les baux actifs à échéance."""
        today = fields.Date.today()
        leases = self.search([
            ('lease_state', '=', '3_progress'),
            ('next_invoice_date', '<=', today),
            ('is_lease', '=', True),
        ])
        _logger.info("Cron Quittances: %d bail(s) à facturer.", len(leases))

        for lease in leases:
            try:
                lease._generate_invoice()
            except Exception as e:
                _logger.error("Erreur génération quittance bail %s : %s", lease.name, str(e))

    def _generate_invoice(self):
        """Génère une quittance (facture client) pour ce bail."""
        self.ensure_one()
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not journal:
            raise UserError(_("Aucun journal de vente trouvé pour la société %s.") % self.env.company.name)

        # Lignes récurrentes
        invoice_lines = []
        for line in self.line_ids.filtered('recurring_invoice'):
            invoice_lines.append((0, 0, {
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))

        # Si pas de lignes, on crée une ligne loyer de base
        if not invoice_lines:
            invoice_lines = [(0, 0, {
                'name': _("Loyer — %s — %s") % (self.property_id.name, self.next_invoice_date),
                'quantity': 1.0,
                'price_unit': self.rent_amount,
            })]

        # Date de la prochaine échéance
        plan = self.plan_id
        next_date = self.next_invoice_date + (plan.billing_period if plan else relativedelta(months=1))
        if plan and plan.billing_first_day:
            next_date = next_date.replace(day=1)

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.tenant_id.id,
            'journal_id': journal.id,
            'invoice_date': self.next_invoice_date,
            'invoice_date_due': self.next_invoice_date,
            'invoice_origin': self.name,
            'narration': _("Quittance de loyer — Bail %s") % self.name,
            'invoice_line_ids': invoice_lines,
        })
        move.action_post()

        # Calcul épargne sur la facture
        self._compute_saving_lines(move)

        # Mettre à jour les dates du bail
        self.write({
            'last_invoice_date': self.next_invoice_date,
            'next_invoice_date': next_date,
        })

        _logger.info("Quittance %s créée pour bail %s.", move.name, self.name)
        return move

    def _compute_saving_lines(self, move):
        """Calcule et attache les lignes d'épargne à la quittance."""
        for rule in self.saving_rule_ids.filtered('is_active'):
            base = move.amount_untaxed if rule.base == 'rent' else move.amount_total
            if rule.mode == 'percent':
                amount = base * (rule.value / 100.0)
            else:
                amount = rule.value

            self.env['account.move.saving.line'].create({
                'move_id': move.id,
                'saving_rule_id': rule.id,
                'base_amount': base,
            })

    # ----------------------------------------------------------------
    #  COMPUTE NEXT_INVOICE_DATE
    # ----------------------------------------------------------------

    @api.depends('start_date', 'plan_id', 'last_invoice_date')
    def _compute_invoice_dates(self):
        for lease in self:
            if not lease.next_invoice_date and lease.start_date:
                plan = lease.plan_id
                if plan and plan.billing_first_day:
                    lease.next_invoice_date = lease.start_date.replace(day=1)
                else:
                    lease.next_invoice_date = lease.start_date
                lease.last_invoice_date = False

    # ----------------------------------------------------------------
    #  CRON : ALERTES EXPIRATION
    # ----------------------------------------------------------------

    @api.model
    def _cron_lease_expiration(self):
        """Alerte les gestionnaires pour les baux expirant dans 60j."""
        today = fields.Date.today()
        warning_date = today + relativedelta(days=60)

        expiring = self.search([
            ('lease_state', '=', '3_progress'),
            ('end_date', '!=', False),
            ('end_date', '<=', warning_date),
            ('end_date', '>=', today),
            ('is_closing', '=', False),
        ])

        for lease in expiring:
            lease.write({'is_closing': True})
            lease.message_post(
                body=_("⚠️ Ce bail arrive à terme le %s. Pensez au renouvellement ou à la résiliation.")
                % lease.end_date,
                message_type='notification',
            )
        _logger.info("Cron Expirations: %d bail(s) notifié(s).", len(expiring))

    # ----------------------------------------------------------------
    #  CRON : PÉNALITÉS AUTO
    # ----------------------------------------------------------------

    @api.model
    def _cron_lease_auto_penalties(self):
        """Génère automatiquement les pénalités sur les factures impayées."""
        today = fields.Date.today()
        active_leases = self.search([('lease_state', '=', '3_progress')])
        count = 0

        for lease in active_leases:
            schedules = lease.schedule_ids.filtered(
                lambda s: s.is_active and s.auto_generate
            ).sorted('trigger_days')
            if not schedules:
                continue

            unpaid_invoices = self.env['account.move'].search([
                ('invoice_origin', 'like', lease.name),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ['paid', 'in_payment']),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date_due', '<', today),
            ])

            for inv in unpaid_invoices:
                days_late = (today - inv.invoice_date_due).days
                for sched in schedules:
                    if days_late >= sched.trigger_days:
                        existing = self.env['re.penalty'].search([
                            ('lease_id', '=', lease.id),
                            ('invoice_id', '=', inv.id),
                            ('schedule_id', '=', sched.id),
                            ('state', '!=', 'cancelled'),
                        ], limit=1)
                        if not existing:
                            self.env['re.penalty'].create({
                                'lease_id': lease.id,
                                'invoice_id': inv.id,
                                'schedule_id': sched.id,
                                'invoice_original_amount': inv.amount_untaxed,
                                'detection_date': today,
                                'state': 'confirmed',
                            })
                            count += 1

        _logger.info("Cron Pénalités auto: %d pénalité(s) créée(s).", count)

    # ----------------------------------------------------------------
    #  WORKFLOW PENALTY
    # ----------------------------------------------------------------

    def action_confirm(self):
        for lease in self.filtered(lambda l: l.is_lease):
            if lease.deposit_amount > 0 and not lease.deposit_paid:
                raise UserError(_("Vous ne pouvez pas confirmer le démarrage de ce bail car la caution de %s %s n'a pas encore été encaissée. Veuillez d'abord générer et encaisser le reçu d'entrée.") % (lease.deposit_amount, lease.currency_id.name))
            if lease.advance_months > 0 and not lease.entry_invoice_paid:
                raise UserError(_("Vous ne pouvez pas confirmer le démarrage de ce bail car l'avance de loyer de %s %s n'a pas encore été payée. Veuillez d'abord générer et encaisser le reçu d'entrée.") % (lease.advance_amount, lease.currency_id.name))

            tenant = lease.tenant_id
            if not tenant.tenant_ref:
                tenant.tenant_ref = self.env['ir.sequence'].next_by_code('re.tenant.ref')
                tenant.tenant_ref_date = fields.Date.today()
            lease.tenant_ref_snapshot = tenant.tenant_ref

            # Log de création
            self.env['re.lease.log'].create({
                'lease_id': lease.id,
                'event_type': '0_creation',
                'event_date': fields.Date.today(),
                'recurring_monthly': lease.rent_amount,
                'amount_signed': lease.rent_amount,
            })

            # Calculer première échéance
            if not lease.next_invoice_date:
                lease._compute_invoice_dates()

            lease.lease_state = '3_progress'

            # Créer automatiquement la ligne loyer si elle n'existe pas
            existing_rent = lease.line_ids.filtered('is_rent_line')
            if not existing_rent:
                rent_product = self.env.ref('maono_real_estate.product_re_rent', raise_if_not_found=False)
                lease.line_ids = [(0, 0, {
                    'name': 'Loyer — %s' % (lease.property_id.name or ''),
                    'product_id': rent_product.product_variant_id.id if rent_product else False,
                    'price_unit': lease.rent_amount,
                    'quantity': 1.0,
                    'recurring_invoice': True,
                    'is_rent_line': True,
                    'sequence': 1,
                })]
        return True

    def action_create_amendment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Avenant de bail'),
            'res_model': 're.lease.amendment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lease_id': self.id,
                'default_new_rent_amount': self.rent_amount,
            }
        }

    @api.model
    def action_reset_demo_data(self):
        """Réinitialise les données de test du module immobilier avec des données 100% cohérentes.
        - Supprime tous les baux, pénalités, règlements, et factures liés à l'immobilier.
        - Crée l'immeuble Palmeraie avec GPS.
        - Crée 3 biens (Appartement 2B, Appartement 3A, Bureau B1).
        - Crée 3 locataires (Marcel Togbe, Kofi Mensah, Ama Diallo).
        - Crée 3 baux correspondants avec historique de factures et paiements de janvier à juillet 2026.
        """
        # 1. Supprimer les anciennes pénalités
        self.env['re.penalty'].search([]).unlink()
        
        # Supprimer les factures et règlements associés aux baux
        moves_to_del = self.env['account.move'].search([
            ('ref', 'like', 'BAIL/'),
        ])
        # Find all payments related to these moves or to leases
        payments_to_del = self.env['account.payment'].search([
            ('ref', 'like', 'BAIL/'),
        ])
        
        # Reconciliation breakdown, draft, cancel, and unlink moves
        if moves_to_del:
            moves_to_del.button_draft()
            # Force unlink of reconcile entries if needed
            self.env['account.partial.reconcile'].search([
                ('debit_move_id', 'in', moves_to_del.mapped('line_ids').ids)
            ]).unlink()
            self.env['account.partial.reconcile'].search([
                ('credit_move_id', 'in', moves_to_del.mapped('line_ids').ids)
            ]).unlink()
            moves_to_del.button_cancel()
            
        if payments_to_del:
            payments_to_del.action_draft()
            payments_to_del.action_cancel()
            payments_to_del.unlink()
            
        if moves_to_del:
            moves_to_del.unlink()

        # Delete leases, properties, buildings
        self.env['re.lease'].search([]).unlink()
        self.env['re.property'].search([]).unlink()
        
        # Delete buildings - we must check and delete the associated automatically created partners!
        buildings = self.env['re.building'].search([])
        partners_to_del = buildings.mapped('partner_id')
        buildings.unlink()
        if partners_to_del:
            partners_to_del.unlink()

        # 2. Créer Immeuble Palmeraie
        # Find country Togo
        country_togo = self.env['res.country'].search([('code', '=', 'TG')], limit=1)
        building = self.env['re.building'].create({
            'name': 'Immeuble Palmeraie',
            'street': 'Boulevard de la Paix',
            'city': 'Lomé',
            'country_id': country_togo.id if country_togo else False,
        })
        # Set GPS on the auto-created partner
        if building.partner_id:
            building.partner_id.write({
                'partner_latitude': 6.13111,
                'partner_longitude': 1.22278,
            })

        # 3. Créer Locataires
        partner_kofi = self.env['res.partner'].create({
            'name': 'Kofi Mensah',
            'is_tenant': True,
            'phone': '+228 90 12 34 56',
            'email': 'kofi.mensah@example.com',
            'street': 'Rue du Commerce',
            'city': 'Lomé',
            'country_id': country_togo.id if country_togo else False,
        })
        partner_marcel = self.env['res.partner'].create({
            'name': 'Marcel Togbe',
            'is_tenant': True,
            'phone': '+228 91 23 45 67',
            'email': 'marcel.togbe@example.com',
            'street': 'Avenue de la Libération',
            'city': 'Lomé',
            'country_id': country_togo.id if country_togo else False,
        })
        partner_ama = self.env['res.partner'].create({
            'name': 'Ama Diallo',
            'is_tenant': True,
            'phone': '+228 92 34 56 78',
            'email': 'ama.diallo@example.com',
            'street': 'Boulevard du Mono',
            'city': 'Lomé',
            'country_id': country_togo.id if country_togo else False,
        })

        # 4. Créer Biens
        prop_3a = self.env['re.property'].create({
            'name': 'Appartement 3A',
            'type': 'residential',
            'building_id': building.id,
            'rent_amount': 150000,
            'state': 'available',
        })
        prop_2b = self.env['re.property'].create({
            'name': 'Appartement 2B',
            'type': 'residential',
            'building_id': building.id,
            'rent_amount': 120000,
            'state': 'available',
        })
        prop_b1 = self.env['re.property'].create({
            'name': 'Bureau B1',
            'type': 'commercial',
            'building_id': building.id,
            'rent_amount': 80000,
            'state': 'available',
        })

        # 5. Créer Baux avec paiements historiques
        # Kofi Mensah (01/01/2026) -> 7 mois payés (Jan, Fév, Mar, Avr, Mai, Juin, Juil)
        self._create_demo_lease(partner_kofi, prop_3a, 150000, 300000, '2026-01-01', 7)
        # Marcel Togbe (01/03/2026) -> 5 mois payés
        self._create_demo_lease(partner_marcel, prop_2b, 120000, 240000, '2026-03-01', 5)
        # Ama Diallo (01/05/2026) -> 3 mois payés
        self._create_demo_lease(partner_ama, prop_b1, 80000, 160000, '2026-05-01', 3)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Données réinitialisées'),
                'message': _('Les données de démonstration ont été nettoyées et reconstruites avec succès.'),
                'type': 'success',
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            }
        }

    def _create_demo_lease(self, tenant, property_obj, rent, deposit, start_date_str, months_to_pay):
        start_date = fields.Date.from_string(start_date_str)
        plan_mensuel = self.env['re.lease.plan'].search([('billing_period', '=', 'monthly')], limit=1)
        if not plan_mensuel:
            plan_mensuel = self.env['re.lease.plan'].create({
                'name': 'Mensuel',
                'billing_period': 'monthly',
            })
            
        lease = self.create({
            'property_id': property_obj.id,
            'tenant_id': tenant.id,
            'rent_amount': rent,
            'deposit_amount': deposit,
            'advance_months': 1,
            'lease_type': 'monthly',
            'plan_id': plan_mensuel.id,
            'start_date': start_date,
            'lease_state': '1_draft',
        })

        # Create entry invoice for advance + deposit, and pay it
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        
        bank_journal = self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        # Generate entry invoice (caution + 1 month advance)
        entry_lines = []
        if deposit > 0:
            deposit_product = self.env.ref('maono_real_estate.product_re_deposit', raise_if_not_found=False)
            entry_lines.append((0, 0, {
                'product_id': deposit_product.product_variant_id.id if deposit_product else False,
                'name': _("Dépôt de garantie (Caution) — Bail %s") % lease.name,
                'quantity': 1.0,
                'price_unit': deposit,
            }))
        if rent > 0:
            rent_product = self.env.ref('maono_real_estate.product_re_rent', raise_if_not_found=False)
            entry_lines.append((0, 0, {
                'product_id': rent_product.product_variant_id.id if rent_product else False,
                'name': _("Avance de loyer (1 mois) — Bail %s") % lease.name,
                'quantity': 1.0,
                'price_unit': rent,
            }))

        entry_invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': tenant.id,
            'journal_id': journal.id,
            'invoice_date': start_date,
            'invoice_date_due': start_date,
            'invoice_origin': lease.name,
            'lease_id': lease.id,
            'is_entry_invoice': True,
            'invoice_period_start': start_date,
            'invoice_period_end': start_date,
            'ref': lease.name,
            'invoice_line_ids': entry_lines,
        })
        entry_invoice.action_post()

        # Register entry payment
        entry_payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_id': tenant.id,
            'amount': rent + deposit,
            'date': start_date,
            'journal_id': bank_journal.id if bank_journal else False,
            'ref': 'Paiement Entrée %s' % entry_invoice.name,
            'lease_id': lease.id,
        })
        entry_payment.action_post()
        (entry_invoice + entry_payment.move_id).line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable').reconcile()

        # Update computed fields to bypass lock
        lease.with_context(bypass_lease_lock=True).write({
            'deposit_paid': True,
            'deposit_paid_date': start_date,
            'entry_invoice_paid': True,
        })

        # Confirm the lease
        lease.action_confirm()

        # Generate paid quittances for the remaining months (from month 2 to months_to_pay)
        current_date = start_date + relativedelta(months=1)
        for m in range(1, months_to_pay):
            period_end = current_date + relativedelta(months=1) - relativedelta(days=1)
            
            quittance = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': tenant.id,
                'journal_id': journal.id,
                'invoice_date': current_date,
                'invoice_date_due': current_date,
                'invoice_origin': lease.name,
                'lease_id': lease.id,
                'invoice_period_start': current_date,
                'invoice_period_end': period_end,
                'ref': lease.name,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Loyer — %s — Période du %s au %s' % (
                        property_obj.name,
                        current_date.strftime('%d/%m/%Y'),
                        period_end.strftime('%d/%m/%Y')
                    ),
                    'quantity': 1.0,
                    'price_unit': rent,
                })]
            })
            quittance.action_post()
            
            pay = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_id': tenant.id,
                'amount': rent,
                'date': current_date,
                'journal_id': bank_journal.id if bank_journal else False,
                'ref': 'Paiement Loyer %s' % quittance.name,
                'lease_id': lease.id,
            })
            pay.action_post()
            (quittance + pay.move_id).line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable').reconcile()
            
            current_date += relativedelta(months=1)

        # Update final next invoice dates
        lease.with_context(bypass_lease_lock=True).write({
            'last_invoice_date': current_date - relativedelta(months=1),
            'next_invoice_date': current_date,
        })
        
        property_obj.write({'state': 'occupied'})
        return lease
