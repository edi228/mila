# -*- coding: utf-8 -*-
from odoo import models, fields

class ReTenantRefLog(models.Model):
    _name = 're.tenant.ref.log'
    _description = 'Historique des modifications de référence locataire'
    _order = 'change_date desc, id desc'

    partner_id = fields.Many2one('res.partner', string="Locataire concerné", required=True, ondelete='cascade')
    old_ref = fields.Char(string="Ancienne référence")
    new_ref = fields.Char(string="Nouvelle référence")
    changed_by = fields.Many2one('res.users', string="Modifié par", default=lambda self: self.env.user)
    change_date = fields.Datetime(string="Date de modification", default=fields.Datetime.now)
    reason = fields.Text(string="Motif de modification", required=True)
