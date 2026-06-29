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

    # ── Rôle immobilier principal (compute = pas de colonne SQL) ───────────
    re_contact_type = fields.Selection([
        ('tenant',   'Locataire'),
        ('owner',    'Propriétaire'),
        ('guarantor','Garant'),
        ('provider', 'Prestataire'),
        ('other',    'Autre'),
    ], string="Rôle immobilier principal",
       compute='_compute_re_contact_type', inverse='_inverse_re_contact_type',
       store=False,
       help="Rôle principal dans la gestion immobilière. Un contact peut cumuler plusieurs rôles.")

    # ── Pièce d'identité (store=False — pas de colonne SQL) ───────────────
    identity_doc_type = fields.Selection([
        ('cni',       "Carte Nationale d'Identité"),
        ('passport',  'Passeport'),
        ('driver',    'Permis de conduire'),
        ('residence', 'Titre de séjour'),
        ('other',     'Autre'),
    ], string="Type de pièce d'identité", store=False)
    identity_doc_number  = fields.Char(string="Numéro de pièce", store=False)
    identity_doc_expiry  = fields.Date(string="Date d'expiration pièce", store=False)
    identity_doc_expired = fields.Boolean(string="Pièce expirée", compute='_compute_identity_expired')
    identity_doc_scan_name      = fields.Char(string="Nom fichier recto", store=False)
    identity_doc_scan_back_name = fields.Char(string="Nom fichier verso", store=False)

    # ── Compute du rôle principal depuis les booléens ─────────────────────
    @api.depends('is_tenant', 'is_property_owner', 'is_guarantor')
    def _compute_re_contact_type(self):
        for p in self:
            if p.is_tenant:
                p.re_contact_type = 'tenant'
            elif p.is_property_owner:
                p.re_contact_type = 'owner'
            elif p.is_guarantor:
                p.re_contact_type = 'guarantor'
            else:
                p.re_contact_type = False

    def _inverse_re_contact_type(self):
        for p in self:
            if p.re_contact_type == 'tenant':
                p.is_tenant = True
            elif p.re_contact_type == 'owner':
                p.is_property_owner = True
            elif p.re_contact_type == 'guarantor':
                p.is_guarantor = True

    @api.depends('identity_doc_expiry')
    def _compute_identity_expired(self):
        today = fields.Date.today()
        for partner in self:
            partner.identity_doc_expired = bool(
                partner.identity_doc_expiry and partner.identity_doc_expiry < today
            )

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

    def action_view_guarantor_leases(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Garanties de %s' % self.name,
            'res_model': 're.lease',
            'view_mode': 'list,form',
            'domain': [('guarantor_id', '=', self.id)],
        }
