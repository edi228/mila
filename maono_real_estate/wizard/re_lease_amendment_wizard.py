# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReLeaseAmendmentWizard(models.TransientModel):
    _name = 're.lease.amendment.wizard'
    _description = 'Wizard Avenant de Bail'

    lease_id = fields.Many2one('re.lease', string="Bail", required=True)
    amendment_type = fields.Selection([
        ('upsell', 'Upsell — Augmentation'),
        ('downsell', 'Downsell — Réduction'),
        ('service_add', 'Ajout de service'),
        ('service_remove', 'Retrait de service'),
    ], string="Type d'avenant", required=True)

    current_rent = fields.Monetary(related='lease_id.rent_amount', string="Loyer actuel", readonly=True)
    new_rent_amount = fields.Monetary(string="Nouveau loyer", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')

    effective_date = fields.Date(string="Date d'effet", required=True, default=fields.Date.context_today)
    reason = fields.Text(string="Motif de l'avenant", required=True)

    lines_to_add_ids = fields.One2many('re.lease.amendment.line', 'wizard_id', string="Services à ajouter")

    def action_apply(self):
        self.ensure_one()
        lease = self.lease_id
        old_rent = lease.rent_amount
        log_details = []

        # Modification loyer
        if self.new_rent_amount and self.new_rent_amount != old_rent:
            rent_line = lease.line_ids.filtered('is_rent_line')
            if rent_line:
                rent_line.price_unit = self.new_rent_amount
                rent_line.name = 'Loyer — %s' % (lease.property_id.name or '')
            lease.rent_amount = self.new_rent_amount
            log_details.append('Loyer : %s → %s %s' % (old_rent, self.new_rent_amount, lease.currency_id.name))

        # Ajout de services
        for line in self.lines_to_add_ids:
            lease.line_ids = [(0, 0, {
                'name': line.name or line.product_id.name,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'recurring_invoice': True,
                'is_rent_line': False,
            })]
            log_details.append('Service ajouté : %s (%s %s/mois)' % (
                line.product_id.name, line.price_unit, lease.currency_id.name))

        # Écriture dans le journal d'événements
        self.env['re.lease.log'].create({
            'lease_id': lease.id,
            'event_type': '7_upsell' if self.amendment_type in ('upsell', 'service_add') else '8_downsell',
            'event_date': self.effective_date,
            'recurring_monthly': lease.lmr,
            'amount_signed': self.new_rent_amount or lease.rent_amount,
            'note': 'Avenant (%s) : %s\nMotif : %s' % (
                dict(self._fields['amendment_type'].selection).get(self.amendment_type),
                ' | '.join(log_details),
                self.reason,
            ),
        })

        # Message dans le chatter
        lease.message_post(
            body='📋 <b>Avenant appliqué</b><br/>Type : %s<br/>Date d\'effet : %s<br/>%s<br/><i>Motif : %s</i>' % (
                dict(self._fields['amendment_type'].selection).get(self.amendment_type),
                self.effective_date,
                '<br/>'.join(log_details),
                self.reason,
            ),
            message_type='comment',
        )

        return {'type': 'ir.actions.act_window_close'}


class ReLeaseAmendmentLine(models.TransientModel):
    _name = 're.lease.amendment.line'
    _description = 'Ligne de service à ajouter (avenant)'

    wizard_id = fields.Many2one('re.lease.amendment.wizard', ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Service",
                                 domain="[('is_rental_service', '=', True)]", required=True)
    name = fields.Char(string="Description")
    price_unit = fields.Monetary(string="Prix", currency_field='currency_id')
    quantity = fields.Float(string="Qté", default=1.0)
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id')
