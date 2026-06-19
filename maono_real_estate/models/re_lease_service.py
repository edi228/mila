# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseService(models.Model):
    _name = 're.lease.service'
    _description = 'Service inclus au bail'

    name = fields.Char(string="Nom du service", required=True)
    category = fields.Selection([
        ('utility', 'Utilité publique (Eau, Elec)'),
        ('security', 'Sécurité / Gardiennage'),
        ('maintenance', 'Entretien / Ménage'),
        ('amenity', 'Équipement partagé (Piscine)'),
        ('other', 'Autre')
    ], string="Catégorie")
    included_by_default = fields.Boolean(string="Inclus par défaut", default=False)
    description = fields.Text(string="Description")
