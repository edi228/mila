# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseLog(models.Model):
    _name = 're.lease.log'
    _description = 'Journal d\'évolution du bail'

    lease_id = fields.Many2one('re.lease', string="Bail", required=True, ondelete='cascade')
    event_type = fields.Selection([
        ('0_creation', 'Création'),
        ('1_expansion', 'Avenant (Hausse)'),
        ('2_contraction', 'Avenant (Baisse)'),
        ('3_churn', 'Résiliation'),
        ('7_upsell', 'Avenant Upsell'),
        ('8_downsell', 'Avenant Downsell'),
    ], string="Type d'événement")
    event_date = fields.Date(string="Date de l'événement")
    
    recurring_monthly = fields.Monetary(string="LMR au moment de l'événement", currency_field='currency_id')
    amount_signed = fields.Monetary(string="Delta LMR", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')
    note = fields.Text(string="Note")
