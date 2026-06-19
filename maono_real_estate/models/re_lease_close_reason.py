# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseCloseReason(models.Model):
    _name = 're.lease.close.reason'
    _description = 'Motif de résiliation de bail'

    name = fields.Char(string="Motif", required=True)
    is_protected = fields.Boolean(string="Protégé par le système", default=False, help="Impossible de supprimer ou modifier si vrai (utilisé par le code).")
