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
    
    deposit_amount = fields.Monetary(string="Dépôt de garantie", tracking=True)
    deposit_paid = fields.Boolean(string="Dépôt encaissé", tracking=True)
    deposit_paid_date = fields.Date(string="Date d'encaissement")
    deposit_returned = fields.Boolean(string="Dépôt restitué", tracking=True)
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
            
            if not lease.is_fully_signed:
                # Warning logic, non-blocking as per spec
                pass
            
            lease.lease_state = '3_progress'
        return True

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
