# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReLeasePenaltySchedule(models.Model):
    _name = 're.lease.penalty.schedule'
    _description = 'Calendrier de pénalités'
    _order = 'sequence, id'

    lease_id = fields.Many2one('re.lease', string="Bail concerné", ondelete='cascade')
    sequence = fields.Integer(string="Séquence", default=10)
    name = fields.Char(string="Libellé", required=True)
    
    trigger_days = fields.Integer(string="Jours APRÈS échéance", required=True)
    mode = fields.Selection([
        ('percent', 'Pourcentage'),
        ('fixed', 'Montant Fixe')
    ], string="Mode de calcul", default='percent', required=True)
    value = fields.Float(string="Valeur (% ou Fixe)", required=True)
    
    base = fields.Selection([
        ('original', 'Montant facture original'),
        ('cumulative', 'Montant cumulatif')
    ], string="Base", default='cumulative', required=True)
    
    is_active = fields.Boolean(string="Active", default=True)
    auto_generate = fields.Boolean(string="Génération auto par Cron", default=True)
    note = fields.Text(string="Conditions")


class RePenalty(models.Model):
    _name = 're.penalty'
    _description = 'Instance de pénalité'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Référence", compute='_compute_name', store=True, tracking=True)
    lease_id = fields.Many2one('re.lease', string="Bail concerné", required=True, tracking=True)
    schedule_id = fields.Many2one('re.lease.penalty.schedule', string="Palier", required=True)
    invoice_id = fields.Many2one('account.move', string="Quittance impayée", required=True)
    
    trigger_days = fields.Integer(related='schedule_id.trigger_days', string="J+ déclenchement")
    base = fields.Selection(related='schedule_id.base', string="Base utilisée")
    
    invoice_original_amount = fields.Monetary(string="Montant HT original", currency_field='currency_id')
    prior_penalties_amount = fields.Monetary(string="Pénalités antérieures", compute='_compute_cumulative_base', currency_field='currency_id')
    cumulative_base = fields.Monetary(string="Base cumulative", compute='_compute_cumulative_base', currency_field='currency_id')
    
    mode = fields.Selection(related='schedule_id.mode', string="Mode calcul")
    rate_or_amount = fields.Float(related='schedule_id.value', string="Valeur appliquée")
    penalty_amount = fields.Monetary(string="Montant de la pénalité", compute='_compute_cumulative_base', store=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('invoiced', 'Facturée'),
        ('cancelled', 'Annulée')
    ], string="Statut", default='draft', tracking=True)
    
    penalty_invoice_id = fields.Many2one('account.move', string="Facture de pénalité", tracking=True)
    
    due_date = fields.Date(related='invoice_id.invoice_date_due', string="Échéance quittance")
    detection_date = fields.Date(string="Date détection", default=fields.Date.context_today)
    days_late = fields.Integer(string="Jours de retard", compute='_compute_days_late')
    
    note = fields.Text(string="Justification")

    @api.depends('create_date')
    def _compute_name(self):
        for record in self:
            if not record.name:
                record.name = self.env['ir.sequence'].next_by_code('re.penalty.seq') or '/'

    @api.depends('invoice_original_amount', 'schedule_id', 'invoice_id')
    def _compute_cumulative_base(self):
        for penalty in self:
            if penalty.lease_id and penalty.invoice_id and penalty.schedule_id:
                prior = self.env['re.penalty'].search([
                    ('lease_id', '=', penalty.lease_id.id),
                    ('invoice_id', '=', penalty.invoice_id.id),
                    ('state', 'in', ['confirmed', 'invoiced']),
                    ('schedule_id.trigger_days', '<', penalty.schedule_id.trigger_days),
                    ('id', '!=', penalty.id)
                ])
                penalty.prior_penalties_amount = sum(prior.mapped('penalty_amount'))
                penalty.cumulative_base = penalty.invoice_original_amount + penalty.prior_penalties_amount
                
                base = penalty.cumulative_base if penalty.base == 'cumulative' else penalty.invoice_original_amount
                
                if penalty.mode == 'percent':
                    penalty.penalty_amount = base * (penalty.rate_or_amount / 100.0)
                else:
                    penalty.penalty_amount = penalty.rate_or_amount
            else:
                penalty.prior_penalties_amount = 0.0
                penalty.cumulative_base = 0.0
                penalty.penalty_amount = 0.0

    @api.depends('due_date')
    def _compute_days_late(self):
        for record in self:
            if record.due_date:
                delta = fields.Date.context_today(self) - record.due_date
                record.days_late = delta.days if delta.days > 0 else 0
            else:
                record.days_late = 0
