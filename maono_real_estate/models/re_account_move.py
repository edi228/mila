# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    lease_saving_ids = fields.One2many('account.move.saving.line', 'move_id', string="Lignes d'épargne calculées")
    total_saving_amount = fields.Monetary(string="Total épargne à provisionner", compute='_compute_total_saving_amount')
    saving_transferred = fields.Boolean(string="Épargne transférée", default=False)
    saving_transfer_date = fields.Date(string="Date du transfert")
    saving_transfer_move_id = fields.Many2one('account.move', string="Écriture de transfert")

    @api.depends('lease_saving_ids.saving_amount')
    def _compute_total_saving_amount(self):
        for move in self:
            move.total_saving_amount = sum(move.lease_saving_ids.mapped('saving_amount'))

class AccountMoveSavingLine(models.Model):
    _name = 'account.move.saving.line'
    _description = "Ligne d'épargne calculée"

    move_id = fields.Many2one('account.move', string="Facture parente", required=True, ondelete='cascade')
    saving_rule_id = fields.Many2one('re.lease.saving.rule', string="Règle appliquée", required=True)
    name = fields.Char(related='saving_rule_id.name', string="Motif")
    
    base_amount = fields.Monetary(string="Base de calcul", currency_field='currency_id')
    saving_amount = fields.Monetary(string="Montant d'épargne", compute='_compute_saving_amount', currency_field='currency_id')
    
    target_account_id = fields.Many2one('account.account', related='saving_rule_id.target_account_id')
    currency_id = fields.Many2one('res.currency', related='move_id.currency_id')
    lease_id = fields.Many2one('re.lease', related='saving_rule_id.lease_id', string="Bail", store=True)

    @api.depends('saving_rule_id', 'base_amount')
    def _compute_saving_amount(self):
        for line in self:
            if line.saving_rule_id:
                if line.saving_rule_id.mode == 'percent':
                    line.saving_amount = line.base_amount * (line.saving_rule_id.value / 100.0)
                else:
                    line.saving_amount = line.saving_rule_id.value
            else:
                line.saving_amount = 0.0
