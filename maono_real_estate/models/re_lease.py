# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class ReLease(models.Model):
    _name = 're.lease'
    _description = 'Contrat de Bail'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'start_date desc, id desc'

    # 3.1 Informations contractuelles
    name = fields.Char(string="Référence du bail", compute='_compute_name', store=True, readonly=True, tracking=True)
    property_id = fields.Many2one('re.property', string="Bien immobilier", required=True, tracking=True)
    owner_id = fields.Many2one('res.partner', related='property_id.owner_id', string="Propriétaire", store=True)
    tenant_id = fields.Many2one('res.partner', string="Locataire principal", required=True, tracking=True)
    tenant_ref_snapshot = fields.Char(string="Réf. Locataire au contrat", copy=False, readonly=True, store=True)
    
    guarantor_id = fields.Many2one('res.partner', string="Garant", tracking=True)
    co_tenant_ids = fields.Many2many('res.partner', string="Co-locataires")
    
    lease_type = fields.Selection([
        ('monthly', 'Mensuel'),
        ('annual', 'Annuel'),
        ('commercial', 'Commercial'),
        ('seasonal', 'Saisonnier')
    ], string="Type de bail", required=True, tracking=True)
    
    plan_id = fields.Many2one('re.lease.plan', string="Plan de récurrence", tracking=True)
    start_date = fields.Date(string="Date de début", required=True, default=fields.Date.context_today, tracking=True)
    end_date = fields.Date(string="Date de fin", tracking=True)
    
    next_invoice_date = fields.Date(string="Prochaine échéance", compute='_compute_invoice_dates', store=True, tracking=True)
    last_invoice_date = fields.Date(string="Dernière quittance", compute='_compute_invoice_dates', store=True)
    first_contract_date = fields.Date(string="Premier bail", compute='_compute_first_contract', store=True)

    # 3.2 Conditions financières
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    rent_amount = fields.Monetary(string="Loyer mensuel de base", required=True, tracking=True)
    
    advance_months = fields.Integer(string="Mois d'avance", default=0, tracking=True)
    advance_amount = fields.Monetary(string="Total avance", compute='_compute_signature_total', store=True)
    
    deposit_amount = fields.Monetary(string="Caution", tracking=True)
    deposit_paid = fields.Boolean(string="Caution encaissée", compute='_compute_deposit_paid', store=True, readonly=False, tracking=True)
    deposit_paid_date = fields.Date(string="Date d'encaissement", compute='_compute_deposit_paid', store=True, readonly=False)
    deposit_returned = fields.Boolean(string="Caution restituée", tracking=True)
    deposit_return_date = fields.Date(string="Date de restitution")
    deposit_deductions = fields.Monetary(string="Déductions sur caution")
    deposit_deduction_note = fields.Text(string="Justification déductions")
    
    signature_total = fields.Monetary(string="Total à la signature", compute='_compute_signature_total', store=True)
    
    indexation_rate = fields.Float(string="Taux d'indexation (%)", tracking=True)
    next_indexation_date = fields.Date(string="Prochaine indexation")

    # 3.3 Services inclus
    service_ids = fields.Many2many('re.lease.service', string="Services inclus")

    # 3.5 États
    lease_state = fields.Selection([
        ('1_draft', 'Devis de bail'),
        ('2_renewal', 'Renouvellement en cours'),
        ('3_progress', 'En cours (Actif)'),
        ('4_paused', 'Suspendu'),
        ('5_renewed', 'Renouvelé'),
        ('6_churn', 'Résilié'),
        ('7_upsell', 'Avenant en cours')
    ], string="Statut", default='1_draft', required=True, tracking=True)

    # 3.6 Fork de sale.subscription
    is_lease = fields.Boolean(string="Est un bail récurrent", default=True)
    payment_token_id = fields.Many2one('payment.token', string="Prélèvement automatique")
    payment_exception = fields.Boolean(string="Défaut de paiement", tracking=True)
    pending_transaction = fields.Boolean(string="Virement en attente")
    is_batch = fields.Boolean(string="Traitement par lot")
    is_invoice_cron = fields.Boolean(string="Généré par le cron")
    
    close_reason_id = fields.Many2one('re.lease.close.reason', string="Motif de résiliation", tracking=True)
    origin_lease_id = fields.Many2one('re.lease', string="Bail d'origine")
    parent_lease_id = fields.Many2one('re.lease', string="Bail parent")
    child_lease_ids = fields.One2many('re.lease', 'parent_lease_id', string="Avenants / Renouvellements")
    
    lmr = fields.Monetary(string="Loyer Mensuel Récurrent", compute='_compute_lmr', store=True, tracking=True)
    recurring_total = fields.Monetary(string="Loyer récurrent total")
    non_recurring_total = fields.Monetary(string="Partie ponctuelle totale")
    kpi_1month_lmr_delta = fields.Monetary(string="Delta LMR 1 Mois")
    kpi_3months_lmr_delta = fields.Monetary(string="Delta LMR 3 Mois")
    
    lease_log_ids = fields.One2many('re.lease.log', 'lease_id', string="Journal d'événements")
    starred = fields.Boolean(string="Bail épinglé")
    starred_user_ids = fields.Many2many('res.users', string="Épinglé par")
    internal_note = fields.Html(string="Note interne")
    
    user_pause_start = fields.Date(string="Début suspension")
    warn_system_closing = fields.Boolean(string="Résiliation système imminente")
    is_closing = fields.Boolean(string="Bail arrivant à terme")
    satisfaction_rate = fields.Float(string="Satisfaction locataire (%)")
    
    user_closable = fields.Boolean(related='plan_id.user_closable')
    user_extend = fields.Boolean(related='plan_id.user_extend')
    user_quantity = fields.Boolean(related='plan_id.user_quantity')

    # Lignes, Taxes, Epargnes, Pénalités
    line_ids = fields.One2many('re.lease.line', 'lease_id', string="Lignes de facturation")
    tax_line_ids = fields.One2many('re.lease.tax.line', 'lease_id', string="Taxes appliquées")
    saving_rule_ids = fields.One2many('re.lease.saving.rule', 'lease_id', string="Règles d'épargne")
    schedule_ids = fields.One2many('re.lease.penalty.schedule', 'lease_id', string="Calendrier des pénalités")
    penalty_ids = fields.One2many('re.penalty', 'lease_id', string="Pénalités générées")
    penalty_count = fields.Integer(string="Pénalités", compute='_compute_penalty_count')
    identity_ids = fields.One2many('re.lease.identity', 'lease_id', string="Pièces d'identité")

    # Invoices, Overdue, Taxes & Savings, Contract template
    invoice_ids = fields.One2many('account.move', 'lease_id', string="Quittances / Reçus")
    invoice_count = fields.Integer(string="Factures/Reçus", compute='_compute_invoice_count')
    is_overdue = fields.Boolean(string="Échéance dépassée", compute='_compute_is_overdue', store=False)
    entry_invoice_paid = fields.Boolean(string="Entrée payée", compute='_compute_entry_invoice_paid', store=True)
    
    total_tax_collected = fields.Monetary(string="Taxes collectées", compute='_compute_totals_collected')
    total_saving_collected = fields.Monetary(string="Épargne collectée", compute='_compute_totals_collected')
    
    contract_template_id = fields.Many2one('re.contract.template', string="Modèle de contrat")
    contract_body = fields.Html(string="Corps du contrat")

    # ── Champs inline Locataire (related natifs res.partner uniquement) ───
    tenant_phone = fields.Char(related='tenant_id.phone', string="Téléphone", readonly=False)
    tenant_email = fields.Char(related='tenant_id.email', string="Email", readonly=False)

    # ── Champs inline Garant ──────────────────────────────────────────────
    guarantor_phone = fields.Char(related='guarantor_id.phone', string="Téléphone garant", readonly=False)
    guarantor_email = fields.Char(related='guarantor_id.email', string="Email garant", readonly=False)


    # État des lieux (Entrée / Sortie)
    checkin_image_ids = fields.Many2many('ir.attachment', relation='re_lease_checkin_rel', string="Photos EDLE")
    checkin_date = fields.Date(string="Date EDL Entrée")
    checkin_note = fields.Html(string="Notes EDLE")
    checkin_done = fields.Boolean(string="EDLE Réalisé")
    
    checkout_image_ids = fields.Many2many('ir.attachment', relation='re_lease_checkout_rel', string="Photos EDLS")
    checkout_date = fields.Date(string="Date EDL Sortie")
    checkout_note = fields.Html(string="Notes EDLS")
    checkout_done = fields.Boolean(string="EDLS Réalisé")

    # Signatures
    signature_tenant = fields.Binary(string="Signature Locataire")
    signature_tenant_date = fields.Date(string="Date Signature Locataire")
    signature_tenant_name = fields.Char(string="Nom Signataire Locataire")
    
    signature_owner = fields.Binary(string="Signature Propriétaire")
    signature_owner_date = fields.Date(string="Date Signature Propriétaire")
    signature_owner_name = fields.Char(string="Nom Signataire Propriétaire")
    
    signature_guarantor = fields.Binary(string="Signature Garant")
    signature_guarantor_date = fields.Date(string="Date Signature Garant")
    
    is_fully_signed = fields.Boolean(string="Entièrement Signé", compute='_compute_is_fully_signed')
    contract_pdf_id = fields.Many2one('ir.attachment', string="Contrat PDF Signé")

    @api.model_create_multi
    def create(self, vals_list):
        leases = super().create(vals_list)
        for lease in leases:
            if lease.tenant_id:
                lease.tenant_id.is_tenant = True
            if lease.owner_id:
                lease.owner_id.is_property_owner = True
        return leases

    @api.depends('create_date')
    def _compute_name(self):
        for record in self:
            if not record.name:
                record.name = self.env['ir.sequence'].next_by_code('re.lease.seq') or '/'

    @api.depends('rent_amount', 'advance_months', 'deposit_amount')
    def _compute_signature_total(self):
        for record in self:
            record.advance_amount = record.rent_amount * record.advance_months
            record.signature_total = record.advance_amount + record.deposit_amount

    @api.depends('start_date')
    def _compute_invoice_dates(self):
        # Mapped from sale.subscription next_invoice_date logic, simplistic for scaffolding
        pass

    @api.depends('start_date')
    def _compute_first_contract(self):
        # Mapped from logic where parent hierarchy determines the beginning of the relationship
        for record in self:
            if not record.origin_lease_id:
                record.first_contract_date = record.start_date
            else:
                record.first_contract_date = record.origin_lease_id.start_date

    @api.depends('rent_amount', 'line_ids.price_subtotal')
    def _compute_lmr(self):
        for record in self:
            record.lmr = sum(record.line_ids.filtered('recurring_invoice').mapped('price_subtotal')) or record.rent_amount

    @api.depends('signature_tenant', 'signature_owner')
    def _compute_is_fully_signed(self):
        for record in self:
            record.is_fully_signed = bool(record.signature_tenant and record.signature_owner)

    @api.depends('penalty_ids')
    def _compute_penalty_count(self):
        for rec in self:
            rec.penalty_count = len(rec.penalty_ids.filtered(lambda p: p.state not in ('cancelled',)))

    @api.onchange('rent_amount')
    def _onchange_rent_amount(self):
        rent_line = self.line_ids.filtered('is_rent_line')
        if rent_line:
            rent_line.price_unit = self.rent_amount
            rent_line.name = 'Loyer — %s' % (self.property_id.name or '')

    def action_confirm(self):
        for lease in self.filtered(lambda l: l.is_lease):
            tenant = lease.tenant_id
            if not tenant.tenant_ref:
                tenant.tenant_ref = self.env['ir.sequence'].next_by_code('re.tenant.ref')
                tenant.tenant_ref_date = fields.Date.today()
            lease.tenant_ref_snapshot = tenant.tenant_ref
            tenant.is_tenant = True
            if lease.owner_id:
                lease.owner_id.is_property_owner = True
            
            if not lease.is_fully_signed:
                # Warning logic, non-blocking as per spec
                pass
            
            lease.lease_state = '3_progress'
            # Init next_invoice_date on confirmation
            if not lease.next_invoice_date:
                lease.next_invoice_date = lease.start_date
        return True

    def action_create_invoice_manual(self):
        """Facturation manuelle — logique similaire au module abonnement.
        
        - Vérifie si une facture a déjà été générée pour la période courante.
        - Si oui : génère pour la période suivante.
        - Si non : génère pour la période courante.
        - Crée toujours une facture en brouillon (confirmé par l'utilisateur).
        """
        self.ensure_one()
        if self.lease_state != '3_progress':
            raise UserError("Seuls les baux actifs peuvent être facturés.")

        today = fields.Date.today()
        invoice_date = self.next_invoice_date or today

        # Déterminer la période de facturation
        plan = self.plan_id
        if plan and plan.billing_period == 'monthly':
            period_end = invoice_date + relativedelta(months=1) - relativedelta(days=1)
            next_date  = invoice_date + relativedelta(months=1)
        elif plan and plan.billing_period == 'quarterly':
            period_end = invoice_date + relativedelta(months=3) - relativedelta(days=1)
            next_date  = invoice_date + relativedelta(months=3)
        elif plan and plan.billing_period == 'biannual':
            period_end = invoice_date + relativedelta(months=6) - relativedelta(days=1)
            next_date  = invoice_date + relativedelta(months=6)
        elif plan and plan.billing_period == 'annual':
            period_end = invoice_date + relativedelta(years=1) - relativedelta(days=1)
            next_date  = invoice_date + relativedelta(years=1)
        else:  # mensuel par défaut
            period_end = invoice_date + relativedelta(months=1) - relativedelta(days=1)
            next_date  = invoice_date + relativedelta(months=1)

        # Lignes de la facture
        invoice_lines = []
        for line in self.line_ids.filtered('recurring_invoice'):
            invoice_lines.append((0, 0, {
                'product_id':  line.product_id.id,
                'name':        '%s — Période du %s au %s' % (
                                   line.name or line.product_id.name,
                                   invoice_date.strftime('%d/%m/%Y'),
                                   period_end.strftime('%d/%m/%Y')
                               ),
                'quantity':    line.product_uom_qty,
                'price_unit':  line.price_unit,
                'tax_ids':     [(6, 0, line.tax_id.ids)],
            }))

        # Si pas de lignes, on crée une ligne loyer simple
        if not invoice_lines:
            invoice_lines = [(0, 0, {
                'name':       'Loyer — Bail %s — Période du %s au %s' % (
                                  self.name,
                                  invoice_date.strftime('%d/%m/%Y'),
                                  period_end.strftime('%d/%m/%Y')
                              ),
                'quantity':   1,
                'price_unit': self.rent_amount,
            })]

        # Création de la facture brouillon
        move_vals = {
            'move_type':       'out_invoice',
            'partner_id':      self.tenant_id.id,
            'invoice_date':    invoice_date,
            'invoice_date_due': next_date - relativedelta(days=1),
            'invoice_line_ids': invoice_lines,
            'narration': (
                'Loyer — Bail : %s\n'
                'Bien : %s\n'
                'Locataire : %s\n'
                'Période : du %s au %s'
            ) % (
                self.name,
                self.property_id.name or '',
                self.tenant_id.name or '',
                invoice_date.strftime('%d/%m/%Y'),
                period_end.strftime('%d/%m/%Y'),
            ),
            'ref': self.name,
        }
        invoice = self.env['account.move'].create(move_vals)

        # Avancer la prochaine date de facturation
        self.next_invoice_date = next_date
        self.last_invoice_date = invoice_date

        # Ouvrir la facture créée
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture — %s' % self.name,
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_pause(self):
        self.write({'lease_state': '4_paused', 'user_pause_start': fields.Date.today()})

    def action_resume(self):
        self.write({'lease_state': '3_progress', 'user_pause_start': False})

    def action_renew_lease(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renouveler le bail',
            'res_model': 're.lease.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lease_id': self.id}
        }

    def action_create_amendment(self):
        # Prepare Upsell Order equivalent
        pass

    @api.model
    def _cron_lease_create_quittance(self):
        # Cron quotidien 06h00
        active_leases = self.search([('lease_state', '=', '3_progress'), ('next_invoice_date', '<=', fields.Date.today())])
        # Generate invoices...
        pass

    @api.model
    def _cron_lease_send_payment_reminder(self):
        pass

    @api.model
    def _cron_lease_expiration(self):
        pass

    @api.model
    def _reopen_paid_churned_subscription(self):
        pass

    @api.depends('next_invoice_date', 'lease_state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for lease in self:
            if lease.lease_state == '3_progress' and lease.next_invoice_date and lease.next_invoice_date < today:
                lease.is_overdue = True
            else:
                lease.is_overdue = False

    @api.depends('invoice_ids.payment_state')
    def _compute_entry_invoice_paid(self):
        for lease in self:
            entry_inv = lease.invoice_ids.filtered(lambda m: m.is_entry_invoice)
            if entry_inv:
                lease.entry_invoice_paid = all(m.payment_state in ('paid', 'in_payment') for m in entry_inv)
            else:
                lease.entry_invoice_paid = lease.advance_months == 0

    @api.depends('invoice_ids.payment_state')
    def _compute_deposit_paid(self):
        for lease in self:
            entry_inv = lease.invoice_ids.filtered(lambda m: m.is_entry_invoice)
            if entry_inv:
                is_paid = all(m.payment_state in ('paid', 'in_payment') for m in entry_inv)
                lease.deposit_paid = is_paid
                if is_paid and not lease.deposit_paid_date:
                    lease.deposit_paid_date = fields.Date.today()
            else:
                if lease.deposit_amount == 0:
                    lease.deposit_paid = True
                    lease.deposit_paid_date = False

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    @api.depends('invoice_ids.state', 'invoice_ids.amount_tax', 'invoice_ids.lease_saving_ids')
    def _compute_totals_collected(self):
        for lease in self:
            posted_invoices = lease.invoice_ids.filtered(lambda m: m.state == 'posted')
            lease.total_tax_collected = sum(posted_invoices.mapped('amount_tax'))
            
            saving_lines = posted_invoices.mapped('lease_saving_ids').filtered(lambda s: s.lease_id == lease)
            lease.total_saving_collected = sum(saving_lines.mapped('saving_amount'))

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Factures / Reçus'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('lease_id', '=', self.id)],
            'context': {'default_lease_id': self.id, 'default_move_type': 'out_invoice'},
        }

    def action_view_collected_taxes(self):
        self.ensure_one()
        tax_lines = self.invoice_ids.filtered(lambda m: m.state == 'posted').mapped('line_ids').filtered(lambda l: l.tax_line_id)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Taxes collectées — %s") % self.name,
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', tax_lines.ids)],
        }

    def action_view_collected_savings(self):
        self.ensure_one()
        saving_lines = self.invoice_ids.filtered(lambda m: m.state == 'posted').mapped('lease_saving_ids')
        return {
            'type': 'ir.actions.act_window',
            'name': _("Lignes d'épargne collectées — %s") % self.name,
            'res_model': 'account.move.saving.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', saving_lines.ids)],
        }

    def action_view_entry_invoice(self):
        self.ensure_one()
        entry_inv = self.invoice_ids.filtered(lambda m: m.is_entry_invoice)
        if entry_inv:
            return {
                'type': 'ir.actions.act_window',
                'name': _("Reçu d'entrée"),
                'res_model': 'account.move',
                'res_id': entry_inv[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        raise UserError(_("Aucun reçu d'entrée trouvé."))

    def action_generate_entry_invoice(self):
        self.ensure_one()
        if self.invoice_ids.filtered(lambda m: m.is_entry_invoice):
            raise UserError(_("Le reçu d'entrée a déjà été généré pour ce bail."))
            
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not journal:
            raise UserError(_("Aucun journal de vente trouvé pour la société."))

        invoice_lines = []
        
        # Line 1: Caution (Deposit)
        if self.deposit_amount > 0:
            deposit_product = self.env.ref('maono_real_estate.product_re_deposit', raise_if_not_found=False)
            invoice_lines.append((0, 0, {
                'product_id': deposit_product.product_variant_id.id if deposit_product else False,
                'name': _("Dépôt de garantie (Caution) — Bail %s") % self.name,
                'quantity': 1.0,
                'price_unit': self.deposit_amount,
            }))
            
        # Line 2: Loyer d'avance (Advance rent)
        if self.advance_months > 0:
            rent_product = self.env.ref('maono_real_estate.product_re_rent', raise_if_not_found=False)
            invoice_lines.append((0, 0, {
                'product_id': rent_product.product_variant_id.id if rent_product else False,
                'name': _("Avance de loyer (%s mois) — Bail %s") % (self.advance_months, self.name),
                'quantity': 1.0,
                'price_unit': self.advance_amount,
            }))
            
        if not invoice_lines:
            raise UserError(_("Le montant de la caution et le mois d'avance doivent être supérieurs à 0 pour générer un reçu d'entrée."))
            
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.tenant_id.id,
            'journal_id': journal.id,
            'invoice_date': self.start_date,
            'invoice_date_due': self.start_date,
            'invoice_origin': self.name,
            'lease_id': self.id,
            'is_entry_invoice': True,
            'invoice_period_start': self.start_date,
            'invoice_period_end': self.start_date,
            'narration': _("Reçu d'entrée (Caution & Avance) — Bail %s") % self.name,
            'invoice_line_ids': invoice_lines,
        })
        
        move.action_post()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _("Reçu d'entrée"),
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.onchange('contract_template_id')
    def _onchange_contract_template(self):
        if self.contract_template_id:
            body = self.contract_template_id.content
            placeholders = {
                '${name}': self.name or '',
                '${property_name}': self.property_id.name or '',
                '${building_name}': self.property_id.building_id.name or '',
                '${building_city}': self.property_id.building_id.city or 'Lomé',
                '${owner_name}': self.owner_id.name or '',
                '${owner_city}': self.owner_id.city or 'Lomé',
                '${tenant_name}': self.tenant_id.name or '',
                '${tenant_city}': self.tenant_id.city or 'Lomé',
                '${tenant_nationality}': self.tenant_id.country_id.demonym or 'Togolaise',
                '${guarantor_name}': self.guarantor_id.name or 'Néant',
                '${rent_amount}': '{:,.0f}'.format(self.rent_amount).replace(',', ' ') if self.rent_amount else '0',
                '${deposit_amount}': '{:,.0f}'.format(self.deposit_amount).replace(',', ' ') if self.deposit_amount else '0',
                '${advance_amount}': '{:,.0f}'.format(self.advance_amount).replace(',', ' ') if self.advance_amount else '0',
                '${advance_months}': str(self.advance_months),
                '${start_date}': self.start_date.strftime('%d/%m/%Y') if self.start_date else '',
                '${end_date}': self.end_date.strftime('%d/%m/%Y') if self.end_date else 'Indéterminée',
                '${signature_total}': '{:,.0f}'.format(self.signature_total).replace(',', ' ') if self.signature_total else '0',
            }
            for key, val in placeholders.items():
                body = body.replace(key, val)
            self.contract_body = body

    def write(self, vals):
        if not self.env.context.get('bypass_lease_lock'):
            locked_fields = [
                'property_id', 'tenant_id', 'rent_amount', 'deposit_amount', 
                'plan_id', 'start_date', 'advance_months', 'lease_type'
            ]
            for lease in self:
                if lease.lease_state not in ('1_draft', '2_renewal'):
                    modified_locked = [f for f in locked_fields if f in vals]
                    if modified_locked:
                        field_labels = [self._fields[f].string for f in modified_locked]
                        raise UserError(_(
                            "Le contrat de bail %s est déjà en cours ou clôturé. "
                            "Vous ne pouvez pas modifier directement les éléments contractuels suivants : %s. "
                            "Veuillez passer par un avenant ou un renouvellement."
                        ) % (lease.name, ', '.join(field_labels)))
        return super(ReLease, self).write(vals)
