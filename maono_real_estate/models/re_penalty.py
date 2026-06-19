# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RePenalty(models.Model):
    _name = 're.penalty'
    _description = 'Pénalité de retard'
    _inherit = ['mail.thread']
    _order = 'detection_date desc, id desc'

    name = fields.Char(string="Référence", readonly=True, default=lambda self: _('Nouveau'))
    lease_id = fields.Many2one('re.lease', string="Bail", required=True, ondelete='cascade', tracking=True)
    invoice_id = fields.Many2one('account.move', string="Facture impayée", tracking=True)
    schedule_id = fields.Many2one('re.lease.penalty.schedule', string="Palier pénalité", tracking=True)

    due_date = fields.Date(string="Date d'échéance", related='invoice_id.invoice_date_due', store=True)
    detection_date = fields.Date(string="Date de détection", default=fields.Date.context_today, tracking=True)
    days_late = fields.Integer(string="Jours de retard", compute='_compute_days_late', store=True)

    invoice_original_amount = fields.Monetary(string="Montant facture HT", tracking=True)
    prior_penalties_amount = fields.Monetary(string="Pénalités antérieures", default=0.0)
    cumulative_base = fields.Monetary(string="Base cumulée", compute='_compute_cumulative_base', store=True)

    mode = fields.Selection(related='schedule_id.mode', string="Mode de calcul", store=True)
    rate_or_amount = fields.Float(related='schedule_id.value', string="Taux / Montant", store=True)
    penalty_amount = fields.Monetary(string="Montant pénalité", compute='_compute_penalty_amount', store=True, tracking=True)

    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('invoiced', 'Facturée'),
        ('cancelled', 'Annulée'),
    ], string="Statut", default='draft', tracking=True)

    penalty_invoice_id = fields.Many2one('account.move', string="Facture pénalité")
    note = fields.Text(string="Justification")

    @api.depends('detection_date', 'due_date')
    def _compute_days_late(self):
        for rec in self:
            if rec.detection_date and rec.due_date:
                delta = rec.detection_date - rec.due_date
                rec.days_late = max(0, delta.days)
            else:
                rec.days_late = 0

    @api.depends('invoice_original_amount', 'prior_penalties_amount')
    def _compute_cumulative_base(self):
        for rec in self:
            rec.cumulative_base = rec.invoice_original_amount + rec.prior_penalties_amount

    @api.depends('cumulative_base', 'mode', 'rate_or_amount')
    def _compute_penalty_amount(self):
        for rec in self:
            if rec.mode == 'percent':
                rec.penalty_amount = rec.cumulative_base * (rec.rate_or_amount / 100.0)
            elif rec.mode == 'fixed':
                rec.penalty_amount = rec.rate_or_amount
            else:
                rec.penalty_amount = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('re.penalty') or _('Nouveau')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_create_invoice(self):
        self.ensure_one()
        if not self.lease_id.tenant_id:
            raise UserError(_("Le bail doit avoir un locataire."))
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.lease_id.tenant_id.id,
            'journal_id': journal.id,
            'invoice_date': fields.Date.today(),
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': _("Pénalité de retard — %s") % self.name,
                'quantity': 1.0,
                'price_unit': self.penalty_amount,
            })],
        })
        move.action_post()
        self.write({'state': 'invoiced', 'penalty_invoice_id': move.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})
