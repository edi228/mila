# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReProperty(models.Model):
    _name = 're.property'
    _description = 'Bien immobilier'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom du bien", required=True, tracking=True)
    ref = fields.Char(string="Référence", compute='_compute_ref', store=True)
    active = fields.Boolean(string="Actif", default=True)
    
    building_id = fields.Many2one('re.building', string="Immeuble parent", tracking=True)
    type = fields.Selection([
        ('residential', 'Résidentiel'),
        ('commercial', 'Commercial'),
        ('terrain', 'Terrain'),
        ('parking', 'Parking'),
        ('mixte', 'Mixte')
    ], string="Type", required=True, tracking=True)
    
    surface = fields.Float(string="Surface (m²)", tracking=True)
    floor = fields.Integer(string="Étage", tracking=True)
    rooms = fields.Integer(string="Pièces", tracking=True)
    bathrooms = fields.Integer(string="Salles de bain")
    furnished = fields.Boolean(string="Meublé", tracking=True)
    
    description = fields.Html(string="Description")
    amenities = fields.Many2many('re.property.amenity', string="Équipements")
    
    owner_id = fields.Many2one('res.partner', string="Propriétaire", tracking=True, domain="[('is_property_owner', '=', True)]")
    
    rent_amount = fields.Monetary(string="Loyer mensuel de référence", tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    state = fields.Selection([
        ('available', 'Disponible'),
        ('occupied', 'Occupé'),
        ('suspended', 'Suspendu'),
        ('works', 'En travaux'),
        ('reserved', 'Réservé')
    ], string="Statut", compute='_compute_state', store=True, tracking=True)
    
    active_lease_id = fields.Many2one('re.lease', string="Bail actif", compute='_compute_active_lease')
    lease_ids = fields.One2many('re.lease', 'property_id', string="Historique des baux")
    lease_count = fields.Integer(string="Nombre de baux", compute='_compute_active_lease')
    
    current_tenant_id = fields.Many2one('res.partner', string="Locataire actuel", compute='_compute_active_lease')
    next_availability = fields.Date(string="Date de disponibilité", compute='_compute_active_lease')
    
    # ── Géolocalisation héritée de l'immeuble ──────────────────────────────
    latitude  = fields.Float(related='building_id.latitude',  string="Latitude",  store=False, digits=(10, 7))
    longitude = fields.Float(related='building_id.longitude', string="Longitude", store=False, digits=(10, 7))
    maps_url  = fields.Char(related='building_id.maps_url',   string="Lien Google Maps")

    image_1920 = fields.Image(string="Photo principale", max_width=1920, max_height=1920)
    image_128  = fields.Image(string="Miniature", related='image_1920', max_width=128, max_height=128, store=True)
    note = fields.Html(string="Notes")


    @api.depends('create_date')
    def _compute_ref(self):
        for record in self:
            if not record.ref:
                record.ref = self.env['ir.sequence'].next_by_code('re.property.seq') or '/'

    @api.depends('lease_ids.lease_state')
    def _compute_active_lease(self):
        for record in self:
            record.lease_count = len(record.lease_ids)
            active_leases = record.lease_ids.filtered(lambda l: l.lease_state == '3_progress')
            if active_leases:
                active = active_leases[0]
                record.active_lease_id = active.id
                record.current_tenant_id = active.tenant_id.id
                record.next_availability = active.end_date
            else:
                record.active_lease_id = False
                record.current_tenant_id = False
                record.next_availability = False

    @api.depends('active_lease_id')
    def _compute_state(self):
        for record in self:
            if record.active_lease_id:
                record.state = 'occupied'
            elif not record.state or record.state == 'occupied':
                record.state = 'available'

    def action_view_leases(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Baux — %s' % self.name,
            'res_model': 're.lease',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
