# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_property_owner = fields.Boolean(string="Propriétaire", default=False)
    is_tenant = fields.Boolean(string="Locataire", default=False)
    is_guarantor = fields.Boolean(string="Garant", default=False)
    
    tenant_ref = fields.Char(string="Référence Locataire", copy=False, readonly=True)
    tenant_ref_date = fields.Date(string="Date de référence", readonly=True)

    owner_property_ids = fields.One2many('re.property', 'owner_id', string="Biens en propriété")
    owner_property_count = fields.Integer(string="Nombre de biens", compute='_compute_owner_property_count')

    tenant_lease_ids = fields.One2many('re.lease', 'tenant_id', string="Baux comme locataire")
    active_lease_count = fields.Integer(string="Baux actifs", compute='_compute_lease_counts')
    lease_count = fields.Integer(string="Total baux", compute='_compute_lease_counts')

    guarantor_lease_ids = fields.One2many('re.lease', 'guarantor_id', string="Baux comme garant")
    
    total_lmr = fields.Monetary(string="Total LMR", compute='_compute_total_lmr', currency_field='currency_id')

    @api.depends('owner_property_ids')
    def _compute_owner_property_count(self):
        for partner in self:
            partner.owner_property_count = len(partner.owner_property_ids)

    @api.depends('tenant_lease_ids.lease_state')
    def _compute_lease_counts(self):
        for partner in self:
            partner.lease_count = len(partner.tenant_lease_ids)
            partner.active_lease_count = len(partner.tenant_lease_ids.filtered(lambda l: l.lease_state == '3_progress'))

    @api.depends('tenant_lease_ids.lease_state', 'tenant_lease_ids.lmr')
    def _compute_total_lmr(self):
        for partner in self:
            active_leases = partner.tenant_lease_ids.filtered(lambda l: l.lease_state == '3_progress')
            partner.total_lmr = sum(active_leases.mapped('lmr'))

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            for partner in self:
                if partner.active_lease_count > 0:
                    raise UserError("Impossible d'archiver un contact avec un bail actif.")
        return super(ResPartner, self).write(vals)

    def action_view_re_properties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biens de %s' % self.name,
            'res_model': 're.property',
            'view_mode': 'list,form',
            'domain': [('owner_id', '=', self.id)],
            'context': {'default_owner_id': self.id},
        }

    def action_view_re_leases(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Baux de %s' % self.name,
            'res_model': 're.lease',
            'view_mode': 'list,form',
            'domain': [('tenant_id', '=', self.id)],
            'context': {'default_tenant_id': self.id},
        }
