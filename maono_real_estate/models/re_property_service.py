# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RePropertyService(models.Model):
    _name = 're.property.service'
    _description = 'Interventions et Travaux'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Intitulé", required=True, tracking=True)
    ref = fields.Char(string="Référence", compute='_compute_ref', store=True)
    
    property_id = fields.Many2one('re.property', string="Bien", required=True, tracking=True)
    lease_id = fields.Many2one('re.lease', string="Bail actif")
    
    service_type = fields.Selection([
        ('repair', 'Réparation'),
        ('maintenance', 'Maintenance'),
        ('renovation', 'Rénovation'),
        ('modification', 'Modification'),
        ('inspection', 'Inspection'),
        ('other', 'Autre')
    ], string="Type d'intervention", tracking=True)
    
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Critique'),
        ('3', 'Bloquant')
    ], string="Priorité", default='0', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Demande'),
        ('submitted', 'Soumise'),
        ('approved', 'Approuvée'),
        ('in_progress', 'En cours'),
        ('pending_validation', 'En attente de validation'),
        ('validated', 'Validée'),
        ('invoiced', 'Facturée'),
        ('done', 'Clôturée'),
        ('cancelled', 'Annulée')
    ], string="Statut", default='draft', tracking=True)

    requested_by = fields.Many2one('res.partner', string="Demandeur", tracking=True)
    requested_date = fields.Datetime(string="Date demande", default=fields.Datetime.now, tracking=True)
    
    approved_by = fields.Many2one('res.users', string="Approuvé par", tracking=True)
    approved_date = fields.Datetime(string="Date approbation", tracking=True)
    
    provider_id = fields.Many2one('res.partner', string="Prestataire", tracking=True)
    planned_date = fields.Date(string="Date planifiée", tracking=True)
    start_date_real = fields.Date(string="Début réel", tracking=True)
    end_date_real = fields.Date(string="Fin réelle", tracking=True)
    
    validated_by = fields.Many2one('res.users', string="Validé par", tracking=True)
    validated_date = fields.Datetime(string="Date validation", tracking=True)
    
    estimated_cost = fields.Monetary(string="Coût estimé", tracking=True)
    actual_cost = fields.Monetary(string="Coût réel", tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    description = fields.Html(string="Travaux demandés")
    work_done_description = fields.Html(string="Travaux réalisés")
    cancellation_reason = fields.Text(string="Motif annulation", tracking=True)
    
    vendor_bill_ids = fields.Many2many('account.move', string="Factures fournisseurs")
    vendor_bill_count = fields.Integer(string="Nombre factures", compute='_compute_vendor_bills')
    total_billed = fields.Monetary(string="Somme facturée", compute='_compute_vendor_bills')
    
    image_before_ids = fields.Many2many('ir.attachment', relation='re_service_img_before_rel', string="Photos AVANT")
    image_after_ids = fields.Many2many('ir.attachment', relation='re_service_img_after_rel', string="Photos APRÈS")
    document_ids = fields.Many2many('ir.attachment', relation='re_service_doc_rel', string="Documents (Devis, PV)")
    note = fields.Html(string="Notes internes")

    @api.depends('create_date')
    def _compute_ref(self):
        for record in self:
            if not record.ref:
                record.ref = self.env['ir.sequence'].next_by_code('re.property.service.seq') or '/'

    @api.depends('vendor_bill_ids')
    def _compute_vendor_bills(self):
        for record in self:
            record.vendor_bill_count = len(record.vendor_bill_ids)
            record.total_billed = sum(record.vendor_bill_ids.mapped('amount_total'))

    # ----------------------------------------------------------------
    #  WORKFLOW
    # ----------------------------------------------------------------

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved', 'approved_by': self.env.user.id, 'approved_date': fields.Datetime.now()})

    def action_start(self):
        self.write({'state': 'in_progress', 'start_date_real': fields.Date.today()})

    def action_validate(self):
        self.write({'state': 'pending_validation'})

    def action_confirm_validation(self):
        self.write({'state': 'validated', 'validated_by': self.env.user.id, 'validated_date': fields.Datetime.now()})

    def action_done(self):
        self.write({'state': 'done', 'end_date_real': fields.Date.today()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures fournisseurs',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
        }
