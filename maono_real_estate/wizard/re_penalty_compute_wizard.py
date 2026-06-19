# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RePenaltyComputeWizard(models.TransientModel):
    _name = 're.penalty.compute.wizard'
    _description = 'Calcul et Génération des Pénalités'

    lease_id = fields.Many2one('re.lease', string="Bail", required=True)
    computation_date = fields.Date(string="Date de calcul", required=True, default=fields.Date.context_today)

    # Résultats de simulation
    preview_line_ids = fields.One2many('re.penalty.compute.preview', 'wizard_id', string="Aperçu des pénalités")
    total_preview = fields.Monetary(string="Total à générer", compute='_compute_total_preview')
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')

    @api.depends('preview_line_ids.penalty_amount')
    def _compute_total_preview(self):
        for wiz in self:
            wiz.total_preview = sum(wiz.preview_line_ids.mapped('penalty_amount'))

    @api.onchange('lease_id', 'computation_date')
    def _onchange_compute_preview(self):
        self.preview_line_ids = [(5,)]
        if not self.lease_id or not self.computation_date:
            return

        lines = []
        # Trouver toutes les factures impayées du bail
        unpaid_invoices = self.env['account.move'].search([
            ('invoice_origin', 'like', self.lease_id.name),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'in_payment']),
            ('move_type', '=', 'out_invoice'),
            ('invoice_date_due', '<', self.computation_date),
        ])

        schedules = self.lease_id.schedule_ids.filtered('is_active').sorted('trigger_days')

        for inv in unpaid_invoices:
            days_late = (self.computation_date - inv.invoice_date_due).days
            for sched in schedules:
                if days_late >= sched.trigger_days:
                    # Vérifier si cette pénalité existe déjà
                    existing = self.env['re.penalty'].search([
                        ('lease_id', '=', self.lease_id.id),
                        ('invoice_id', '=', inv.id),
                        ('schedule_id', '=', sched.id),
                        ('state', '!=', 'cancelled'),
                    ], limit=1)
                    if not existing:
                        amount = inv.amount_untaxed
                        if sched.mode == 'percent':
                            penalty = amount * (sched.value / 100.0)
                        else:
                            penalty = sched.value
                        lines.append((0, 0, {
                            'invoice_id': inv.id,
                            'schedule_id': sched.id,
                            'invoice_amount': amount,
                            'days_late': days_late,
                            'penalty_amount': penalty,
                        }))

        self.preview_line_ids = lines

    def action_generate_penalties(self):
        self.ensure_one()
        count = 0
        for line in self.preview_line_ids:
            self.env['re.penalty'].create({
                'lease_id': self.lease_id.id,
                'invoice_id': line.invoice_id.id,
                'schedule_id': line.schedule_id.id,
                'invoice_original_amount': line.invoice_amount,
                'detection_date': self.computation_date,
                'state': 'draft',
            })
            count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Pénalités générées'),
                'message': _('%d pénalité(s) créée(s) avec succès.') % count,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class RePenaltyComputePreview(models.TransientModel):
    _name = 're.penalty.compute.preview'
    _description = 'Aperçu pénalité (wizard)'

    wizard_id = fields.Many2one('re.penalty.compute.wizard', ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string="Facture")
    schedule_id = fields.Many2one('re.lease.penalty.schedule', string="Palier")
    invoice_amount = fields.Monetary(string="Montant facture")
    days_late = fields.Integer(string="Jours de retard")
    penalty_amount = fields.Monetary(string="Pénalité calculée")
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')
