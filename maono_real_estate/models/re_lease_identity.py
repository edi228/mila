# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReLeaseIdentity(models.Model):
    _name = 're.lease.identity'
    _description = 'Pièces d\'identité des parties'

    lease_id = fields.Many2one('re.lease', string="Bail", required=True, ondelete='cascade')
    party = fields.Selection([
        ('tenant', 'Locataire'),
        ('owner', 'Propriétaire'),
        ('guarantor', 'Garant'),
        ('co_tenant', 'Co-locataire')
    ], string="Partie concernée", required=True)
    
    partner_id = fields.Many2one('res.partner', string="Contact", required=True)
    
    doc_type = fields.Selection([
        ('national_id', 'Carte Nationale d\'Identité'),
        ('passport', 'Passeport'),
        ('residence_permit', 'Titre de Séjour'),
        ('driver_license', 'Permis de conduire'),
        ('other', 'Autre')
    ], string="Type de document", required=True)
    
    doc_number = fields.Char(string="Numéro du document", required=True)
    issued_by = fields.Char(string="Autorité émettrice")
    
    issue_date = fields.Date(string="Date d'émission")
    expiry_date = fields.Date(string="Date d'expiration")
    is_valid = fields.Boolean(string="Est valide", compute='_compute_is_valid')
    
    attachment_id = fields.Many2one('ir.attachment', string="Scan Recto")
    attachment_back_id = fields.Many2one('ir.attachment', string="Scan Verso")
    
    verified = fields.Boolean(string="Document vérifié")
    verified_by = fields.Many2one('res.users', string="Vérifié par")
    verified_date = fields.Date(string="Date de vérification")
    
    note = fields.Text(string="Observations")

    @api.depends('expiry_date')
    def _compute_is_valid(self):
        for record in self:
            if record.expiry_date:
                record.is_valid = record.expiry_date > fields.Date.context_today(self)
            else:
                record.is_valid = True
