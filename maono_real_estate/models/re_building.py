# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReBuilding(models.Model):
    _name = 're.building'
    _description = 'Immeuble / Complexe'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", required=True)
    ref  = fields.Char(string="Référence", compute='_compute_ref', store=True)

    # ── Adresse manuelle (conservée pour rétrocompatibilité) ─────────────
    street     = fields.Char(string="Rue")
    street2    = fields.Char(string="Rue 2")
    city       = fields.Char(string="Ville")
    zip        = fields.Char(string="Code postal")
    country_id = fields.Many2one('res.country', string="Pays")

    # ── Contact lié (propriétaire / gestionnaire) ─────────────────────────
    owner_id = fields.Many2one(
        'res.partner', string="Propriétaire",
        domain="[('is_property_owner', '=', True)]",
        tracking=True,
    )

    # ── Contact de géolocalisation ───────────────────────────────────────────
    geo_partner_id = fields.Many2one(
        'res.partner', string="Contact / Localisation",
        help="Sélectionnez un contact dont les coordonnées GPS seront utilisées "
             "pour localiser cet immeuble sur la carte.",
        tracking=True,
    )
    latitude  = fields.Float(
        string="Latitude", digits=(10, 7),
        compute='_compute_geo', store=False,
    )
    longitude = fields.Float(
        string="Longitude", digits=(10, 7),
        compute='_compute_geo', store=False,
    )
    maps_url = fields.Char(
        string="Lien Google Maps",
        compute='_compute_maps_url',
    )

    # ── Stats ──────────────────────────────────────────────────────────────
    property_ids          = fields.One2many('re.property', 'building_id', string="Biens dans cet immeuble")
    property_count        = fields.Integer(string="Nombre total de biens", compute='_compute_properties_stats')
    occupied_count        = fields.Integer(string="Biens occupés",         compute='_compute_properties_stats')
    available_count       = fields.Integer(string="Biens libres",          compute='_compute_properties_stats')
    occupation_rate       = fields.Float(string="Taux d'occupation (%)",   compute='_compute_properties_stats')
    expected_monthly_revenue = fields.Monetary(
        string="Revenu mensuel attendu", compute='_compute_expected_revenue',
    )
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    image_ids = fields.Many2many('ir.attachment', string="Photos")
    note      = fields.Html(string="Description / Notes")
    active    = fields.Boolean(default=True)

    @api.depends('create_date')
    def _compute_ref(self):
        for record in self:
            if not record.ref:
                record.ref = self.env['ir.sequence'].next_by_code('re.building.seq') or '/'

    @api.depends('geo_partner_id.partner_latitude', 'geo_partner_id.partner_longitude')
    def _compute_geo(self):
        for b in self:
            if b.geo_partner_id and (b.geo_partner_id.partner_latitude or b.geo_partner_id.partner_longitude):
                b.latitude  = b.geo_partner_id.partner_latitude
                b.longitude = b.geo_partner_id.partner_longitude
            # Si coordonnées saisies manuellement (champs readonly=False), on les conserve

    @api.depends('latitude', 'longitude')
    def _compute_maps_url(self):
        for b in self:
            if b.latitude and b.longitude:
                b.maps_url = f"https://maps.google.com/?q={b.latitude},{b.longitude}"
            elif b.street and b.city:
                addr = f"{b.street}, {b.city}".replace(' ', '+')
                b.maps_url = f"https://maps.google.com/?q={addr}"
            else:
                b.maps_url = False

    @api.depends('property_ids.state')
    def _compute_properties_stats(self):
        for b in self:
            properties     = b.property_ids
            b.property_count  = len(properties)
            b.occupied_count  = len(properties.filtered(lambda p: p.state == 'occupied'))
            b.available_count = len(properties.filtered(lambda p: p.state == 'available'))
            b.occupation_rate = (b.occupied_count / b.property_count * 100) if b.property_count > 0 else 0.0

    @api.depends('property_ids.rent_amount')
    def _compute_expected_revenue(self):
        for b in self:
            b.expected_monthly_revenue = sum(b.property_ids.mapped('rent_amount'))

    def action_view_properties(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biens — %s' % self.name,
            'res_model': 're.property',
            'view_mode': 'list,form,kanban',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id},
        }

    def action_open_maps(self):
        """Ouvre Google Maps dans un nouvel onglet."""
        self.ensure_one()
        if self.maps_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.maps_url,
                'target': 'new',
            }
