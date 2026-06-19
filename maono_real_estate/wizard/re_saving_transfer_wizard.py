# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReSavingTransferWizard(models.TransientModel):
    _name = 're.saving.transfer.wizard'
    _description = "Transfert de l'épargne provisionnée"

    move_id = fields.Many2one('account.move', string="Quittance source", required=True)
    lease_id = fields.Many2one('re.lease', string="Bail", compute='_compute_lease_id', store=False)

    @api.depends('move_id')
    def _compute_lease_id(self):
        for wiz in self:
            saving_lines = wiz.move_id.lease_saving_ids if wiz.move_id else self.env['account.move.saving.line']
            leases = saving_lines.mapped('lease_id')
            wiz.lease_id = leases[:1] if leases else False

    saving_line_ids = fields.Many2many(
        'account.move.saving.line', string="Lignes à transférer",
        domain="[('move_id', '=', move_id)]"
    )

    journal_id = fields.Many2one('account.journal', string="Journal comptable", required=True,
                                 domain="[('type', 'in', ['bank','cash'])]")
    transfer_date = fields.Date(string="Date du transfert", required=True, default=fields.Date.context_today)
    note = fields.Text(string="Référence / Notes")

    total_saving_amount = fields.Monetary(string="Total à transférer", compute='_compute_total')
    currency_id = fields.Many2one('res.currency', related='move_id.currency_id')

    @api.depends('saving_line_ids')
    def _compute_total(self):
        for wiz in self:
            wiz.total_saving_amount = sum(wiz.saving_line_ids.mapped('saving_amount'))

    @api.onchange('move_id')
    def _onchange_move(self):
        if self.move_id:
            self.saving_line_ids = self.move_id.lease_saving_ids

    def action_transfer(self):
        self.ensure_one()
        if not self.saving_line_ids:
            raise UserError(_("Aucune ligne d'épargne sélectionnée."))
        if self.total_saving_amount <= 0:
            raise UserError(_("Le montant total à transférer doit être positif."))

        # Créer l'écriture de transfert
        move_lines = []
        for line in self.saving_line_ids:
            if not line.target_account_id:
                raise UserError(_("La ligne '%s' n'a pas de compte cible défini.") % line.name)
            # Débit du compte d'épargne → Crédit du compte bancaire
            move_lines.append((0, 0, {
                'account_id': line.target_account_id.id,
                'name': line.name,
                'debit': 0.0,
                'credit': line.saving_amount,
            }))

        move_lines.append((0, 0, {
            'account_id': self.journal_id.default_account_id.id,
            'name': self.note or _("Transfert épargne — %s") % self.move_id.name,
            'debit': self.total_saving_amount,
            'credit': 0.0,
        }))

        transfer_move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': self.journal_id.id,
            'date': self.transfer_date,
            'ref': self.note or _("Transfert épargne — %s") % self.move_id.name,
            'line_ids': move_lines,
        })
        transfer_move.action_post()

        # Marquer la facture source
        self.move_id.write({
            'saving_transferred': True,
            'saving_transfer_date': self.transfer_date,
            'saving_transfer_move_id': transfer_move.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Écriture de transfert"),
            'res_model': 'account.move',
            'res_id': transfer_move.id,
            'view_mode': 'form',
        }
