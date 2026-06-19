# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReLeaseCloseWizard(models.TransientModel):
    _name = 're.lease.close.wizard'
    _description = 'Wizard de Clôture / Résiliation'

    lease_id = fields.Many2one('re.lease', string="Bail à clôturer", required=True)
    tenant_id = fields.Many2one(related='lease_id.tenant_id', readonly=True)
    property_id = fields.Many2one(related='lease_id.property_id', readonly=True)

    close_reason_id = fields.Many2one('re.lease.close.reason', string="Motif de résiliation", required=True)
    close_date = fields.Date(string="Date de résiliation", required=True, default=fields.Date.context_today)

    deposit_returned = fields.Boolean(string="Dépôt de garantie restitué", default=False)
    deposit_deductions = fields.Monetary(string="Déductions sur caution", default=0.0)
    deposit_deduction_note = fields.Text(string="Justification des déductions")
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')

    checkout_done = fields.Boolean(string="EDL Sortie réalisé", default=False)
    checkout_note = fields.Text(string="Notes EDL Sortie")

    note = fields.Text(string="Observations de résiliation")

    def action_close(self):
        self.ensure_one()
        lease = self.lease_id

        if lease.lease_state == '6_churn':
            raise UserError(_("Ce bail est déjà résilié."))

        # Vérifier s'il y a des factures impayées
        unpaid_invoices = self.env['account.move'].search([
            ('invoice_origin', 'like', lease.name),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'in_payment']),
            ('move_type', '=', 'out_invoice'),
        ])
        if unpaid_invoices:
            lease.message_post(
                body=_("⚠️ Résiliation avec %d facture(s) impayée(s). À régulariser.") % len(unpaid_invoices)
            )

        vals = {
            'lease_state': '6_churn',
            'close_reason_id': self.close_reason_id.id,
            'end_date': self.close_date,
            'deposit_returned': self.deposit_returned,
            'deposit_deductions': self.deposit_deductions,
            'deposit_deduction_note': self.deposit_deduction_note,
        }

        if self.checkout_done:
            vals['checkout_done'] = True
            vals['checkout_date'] = self.close_date
            if self.checkout_note:
                vals['checkout_note'] = self.checkout_note

        lease.write(vals)

        # Libérer le bien
        if lease.property_id.state == 'occupied':
            lease.property_id._compute_state()

        # Log
        lease.message_post(
            body=_("Bail résilié le %s. Motif : %s") % (self.close_date, self.close_reason_id.name)
        )

        return {'type': 'ir.actions.act_window_close'}
