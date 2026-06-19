# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RePropertyAmenity(models.Model):
    _name = 're.property.amenity'
    _description = 'Équipement du bien'

    name = fields.Char(string="Nom de l'équipement", required=True)
    description = fields.Text(string="Description")
