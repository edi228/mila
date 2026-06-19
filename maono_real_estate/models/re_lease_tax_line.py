# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReLeaseTaxLine(models.Model):
    _name = 're.lease.tax.line'
    _description = 'Ligne de taxe activée sur un bail'

    lease_id = fields.Many2one('re.lease', string="Bail concerné", ondelete='cascade')
    tax_id = fields.Many2one('account.tax', string="Taxe", domain="[('is_real_estate_tax', '=', True)]", required=True)
    is_active = fields.Boolean(string="Active", default=True)
    
    tax_bearer = fields.Selection(related='tax_id.tax_bearer', readonly=False, store=True)
    tenant_share_percent = fields.Float(string="% Locataire", related='tax_id.tenant_share_percent', readonly=False, store=True)
    owner_share_percent = fields.Float(string="% Propriétaire", compute='_compute_owner_share_percent')
    
    tax_amount_tenant = fields.Monetary(string="Montant Locataire / Période", compute='_compute_tax_amounts')
    tax_amount_owner = fields.Monetary(string="Montant Propriétaire / Période", compute='_compute_tax_amounts')
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')
    
    declaration_periodicity = fields.Selection(related='tax_id.declaration_periodicity', store=True)
    next_declaration_date = fields.Date(string="Prochaine déclaration")
    note = fields.Text(string="Remarque")

    @api.depends('tax_bearer', 'tenant_share_percent')
    def _compute_owner_share_percent(self):
        for line in self:
            if line.tax_bearer == 'shared':
                line.owner_share_percent = 100.0 - line.tenant_share_percent
            elif line.tax_bearer == 'owner':
                line.owner_share_percent = 100.0
            else:
                line.owner_share_percent = 0.0

    @api.depends('lease_id.rent_amount', 'tax_id', 'tenant_share_percent', 'owner_share_percent')
    def _compute_tax_amounts(self):
        for line in self:
            # Simplification: we compute the baseline tax amount based on the rent amount
            rent = line.lease_id.rent_amount if line.lease_id else 0.0
            total_tax = rent * (line.tax_id.amount / 100) if line.tax_id and line.tax_id.amount_type == 'percent' else line.tax_id.amount
            
            if line.tax_bearer == 'tenant':
                line.tax_amount_tenant = total_tax
                line.tax_amount_owner = 0.0
            elif line.tax_bearer == 'owner':
                line.tax_amount_tenant = 0.0
                line.tax_amount_owner = total_tax
            else:
                line.tax_amount_tenant = total_tax * (line.tenant_share_percent / 100)
                line.tax_amount_owner = total_tax * (line.owner_share_percent / 100)
