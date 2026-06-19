# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_rental_service = fields.Boolean(
        string="Service locatif immobilier",
        default=False,
        help="Cocher pour que ce produit apparaisse dans les lignes de services des baux immobiliers."
    )
