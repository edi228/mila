# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseSavingRule(models.Model):
    _name = 're.lease.saving.rule'
    _description = 'Règle d\'épargne'

    lease_id = fields.Many2one('re.lease', string="Bail concerné", ondelete='cascade')
    name = fields.Char(string="Motif", required=True)
    mode = fields.Selection([
        ('percent', 'Pourcentage'),
        ('fixed', 'Montant Fixe')
    ], string="Mode", default='percent', required=True)
    value = fields.Float(string="Valeur (% ou Fixe)", required=True)
    
    base = fields.Selection([
        ('rent', 'Loyer seul'),
        ('total_invoice', 'Total facture')
    ], string="Base de calcul", default='rent', required=True)
    
    is_active = fields.Boolean(string="Active", default=True)
    target_account_id = fields.Many2one('account.account', string="Compte cible (Trésorerie)")
    
    beneficiary = fields.Selection([
        ('owner', 'Propriétaire'),
        ('tenant', 'Locataire'),
        ('other', 'Autre')
    ], string="Bénéficiaire", default='owner')
    beneficiary_partner_id = fields.Many2one('res.partner', string="Contact bénéficiaire")
    
    note = fields.Text(string="Conditions de la règle")
