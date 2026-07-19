# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseTemplate(models.Model):
    _name = 're.lease.template'
    _description = 'Modèle de bail'
    
    name = fields.Char(string="Nom du modèle", required=True)
    plan_id = fields.Many2one('re.lease.plan', string="Plan de facturation", required=True)
    
    service_ids = fields.Many2many('re.lease.service', string="Services inclus par défaut")
    
    advance_months = fields.Integer(string="Mois d'avance par défaut", default=0)
    deposit_months = fields.Integer(string="Mois de caution par défaut", default=1)
    
    active = fields.Boolean(default=True)

class ReContractTemplate(models.Model):
    _name = 're.contract.template'
    _description = 'Modèles de contrats de bails'

    name = fields.Char(string="Nom du modèle", required=True)
    content = fields.Html(string="Contenu du contrat (avec placeholders)", required=True)
    active = fields.Boolean(default=True)
