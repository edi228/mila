# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseLine(models.Model):
    _name = 're.lease.line'
    _description = 'Ligne de contrat de bail'
    _order = 'sequence, id'

    lease_id = fields.Many2one('re.lease', string="Bail", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Séquence", default=10)
    
    product_id = fields.Many2one('product.product', string="Article")
    name = fields.Text(string="Description", required=True)
    
    quantity = fields.Float(string="Quantité", default=1.0, required=True)
    price_unit = fields.Monetary(string="Prix Unitaire", required=True)
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')
    
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    
    recurring_invoice = fields.Boolean(string="Facturation récurrente", default=True)
    allow_one_time_sale = fields.Boolean(string="Facturation ponctuelle", default=False)
    is_rent_line = fields.Boolean(string="Ligne loyer principal", default=False, readonly=True)
    
    price_subtotal = fields.Monetary(string="Sous-total", compute='_compute_amount', store=True)

    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

