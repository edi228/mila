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
