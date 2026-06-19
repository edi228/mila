# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_real_estate_tax = fields.Boolean(string="Taxe Immobilière", default=False)
    tax_bearer = fields.Selection([
        ('tenant', 'Locataire (sur facteur loyer)'),
        ('owner', 'Propriétaire (facture séparée)'),
        ('shared', 'Partagé')
    ], string="À charge de", default='tenant')
    
    tenant_share_percent = fields.Float(string="% à charge du locataire", default=100.0)
    owner_share_percent = fields.Float(string="% à charge du propriétaire", compute='_compute_owner_share')
    
    declaration_periodicity = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('semiannual', 'Semestrielle'),
        ('annual', 'Annuelle')
    ], string="Périodicité de déclaration")
    
    declaration_journal_id = fields.Many2one('account.journal', string="Journal de déclaration propriétaire")
    
    tax_category = fields.Selection([
        ('vat', 'TVA'),
        ('rental_tax', 'Taxe Foncière/Habitation'),
        ('withholding', 'Retenue à la source'),
        ('stamp', 'Droit de timbre'),
        ('other', 'Autre')
    ], string="Catégorie de taxe")
    
    note = fields.Text(string="Base légale et conditions")

    def _compute_owner_share(self):
        for tax in self:
            if tax.tax_bearer == 'shared':
                tax.owner_share_percent = 100.0 - tax.tenant_share_percent
            elif tax.tax_bearer == 'owner':
                tax.owner_share_percent = 100.0
            else:
                tax.owner_share_percent = 0.0
