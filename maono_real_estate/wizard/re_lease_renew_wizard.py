# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ReLeaseRenewWizard(models.TransientModel):
    _name = 're.lease.renew.wizard'
    _description = 'Wizard de Renouvellement de bail'

    lease_id = fields.Many2one('re.lease', string="Bail actuel", required=True)
    tenant_id = fields.Many2one(related='lease_id.tenant_id', readonly=True)
    property_id = fields.Many2one(related='lease_id.property_id', readonly=True)

    new_start_date = fields.Date(string="Nouvelle date de début", required=True,
                                 default=fields.Date.context_today)
    new_end_date = fields.Date(string="Nouvelle date de fin")
    new_rent_amount = fields.Monetary(string="Nouveau loyer mensuel")
    currency_id = fields.Many2one('res.currency', related='lease_id.currency_id')

    copy_tax_lines = fields.Boolean(string="Conserver les taxes", default=True)
    copy_saving_rules = fields.Boolean(string="Conserver les règles d'épargne", default=True)
    copy_penalty_schedules = fields.Boolean(string="Conserver le calendrier des pénalités", default=True)
    copy_services = fields.Boolean(string="Conserver les services inclus", default=True)

    note = fields.Text(string="Commentaire de renouvellement")

    @api.onchange('lease_id')
    def _onchange_lease(self):
        if self.lease_id:
            self.new_rent_amount = self.lease_id.rent_amount
            if self.lease_id.end_date:
                self.new_start_date = self.lease_id.end_date + relativedelta(days=1)

    def action_renew(self):
        self.ensure_one()
        old_lease = self.lease_id

        if old_lease.lease_state not in ('3_progress', '4_paused'):
            raise UserError(_("Seul un bail actif ou suspendu peut être renouvelé."))

        # Création du nouveau bail
        vals = {
            'property_id': old_lease.property_id.id,
            'tenant_id': old_lease.tenant_id.id,
            'guarantor_id': old_lease.guarantor_id.id,
            'co_tenant_ids': [(6, 0, old_lease.co_tenant_ids.ids)],
            'lease_type': old_lease.lease_type,
            'plan_id': old_lease.plan_id.id,
            'start_date': self.new_start_date,
            'end_date': self.new_end_date,
            'rent_amount': self.new_rent_amount or old_lease.rent_amount,
            'deposit_amount': old_lease.deposit_amount,
            'advance_months': old_lease.advance_months,
            'lease_state': '1_draft',
            'parent_lease_id': old_lease.id,
            'origin_lease_id': old_lease.origin_lease_id.id or old_lease.id,
            'currency_id': old_lease.currency_id.id,
        }

        if self.copy_services:
            vals['service_ids'] = [(6, 0, old_lease.service_ids.ids)]

        new_lease = self.env['re.lease'].create(vals)

        # Copie lignes
        for line in old_lease.line_ids:
            line.copy({'lease_id': new_lease.id})

        # Copie taxes
        if self.copy_tax_lines:
            for tax in old_lease.tax_line_ids:
                tax.copy({'lease_id': new_lease.id})

        # Copie règles épargne
        if self.copy_saving_rules:
            for rule in old_lease.saving_rule_ids:
                rule.copy({'lease_id': new_lease.id})

        # Copie calendrier pénalités
        if self.copy_penalty_schedules:
            for sched in old_lease.schedule_ids:
                sched.copy({'lease_id': new_lease.id})

        # Marquer l'ancien bail comme renouvelé
        old_lease.write({'lease_state': '5_renewed'})

        # Log
        old_lease.message_post(
            body=_("Bail renouvelé. Nouveau bail créé : %s") % new_lease.name
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Bail renouvelé'),
            'res_model': 're.lease',
            'res_id': new_lease.id,
            'view_mode': 'form',
        }
