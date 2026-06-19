# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta


class ReDashboard(models.Model):
    _name = 're.dashboard'
    _description = 'Dashboard Immobilier'

    @api.model
    def get_dashboard_data(self):
        """Point d'entrée RPC pour le dashboard OWL."""
        today = date.today()
        LeaseModel = self.env['re.lease']
        PropertyModel = self.env['re.property']
        ServiceModel = self.env['re.property.service']
        PenaltyModel = self.env['re.penalty']
        MoveModel = self.env['account.move']

        # --- KPIs ---
        total_properties = PropertyModel.search_count([])
        occupied = PropertyModel.search_count([('state', '=', 'occupied')])
        available = PropertyModel.search_count([('state', '=', 'available')])
        in_works = PropertyModel.search_count([('state', '=', 'works')])
        occupation_rate = round((occupied / total_properties * 100), 1) if total_properties else 0

        active_leases = LeaseModel.search([('lease_state', '=', '3_progress')])
        lmr_global = sum(active_leases.mapped('lmr'))

        unpaid_invoices = MoveModel.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'in_payment']),
            ('invoice_date_due', '<', today),
        ])
        unpaid_amount = sum(unpaid_invoices.mapped('amount_residual'))
        unpaid_count = len(unpaid_invoices)

        active_penalties = PenaltyModel.search([('state', 'not in', ['cancelled', 'invoiced'])])
        penalty_amount = sum(active_penalties.mapped('penalty_amount'))
        penalty_count = len(active_penalties)

        # --- Baux actifs ---
        leases_data = []
        for lease in active_leases.sorted('next_invoice_date'):
            days_remaining = (lease.end_date - today).days if lease.end_date else None
            color = 'green'
            if days_remaining is not None:
                if days_remaining < 30:
                    color = 'red'
                elif days_remaining < 60:
                    color = 'orange'
            leases_data.append({
                'id': lease.id,
                'name': lease.name,
                'property': lease.property_id.name,
                'property_id': lease.property_id.id,
                'tenant': lease.tenant_id.name,
                'rent': lease.lmr,
                'currency': lease.currency_id.symbol,
                'state': lease.lease_state,
                'next_invoice': str(lease.next_invoice_date) if lease.next_invoice_date else '',
                'end_date': str(lease.end_date) if lease.end_date else '',
                'days_remaining': days_remaining,
                'days_color': color,
                'payment_exception': lease.payment_exception,
            })

        # --- Interventions en cours ---
        active_services = ServiceModel.search([
            ('state', 'not in', ['done', 'cancelled']),
        ], order='priority desc, planned_date asc', limit=20)
        services_data = []
        for svc in active_services:
            services_data.append({
                'id': svc.id,
                'name': svc.name,
                'property': svc.property_id.name if svc.property_id else '',
                'property_id': svc.property_id.id if svc.property_id else False,
                'service_type': svc.service_type,
                'priority': svc.priority,
                'state': svc.state,
                'planned_date': str(svc.planned_date) if svc.planned_date else '',
                'contractor': svc.provider_id.name if svc.provider_id else '',
            })

        # --- Alertes ---
        alerts = []
        # Baux expirant dans 60 jours
        expiring_threshold = today + timedelta(days=60)
        expiring = LeaseModel.search([
            ('lease_state', '=', '3_progress'),
            ('end_date', '!=', False),
            ('end_date', '<=', expiring_threshold),
        ])
        for l in expiring:
            days = (l.end_date - today).days
            alerts.append({
                'type': 'expiry',
                'icon': 'fa-clock-o',
                'color': 'red' if days < 30 else 'orange',
                'message': f'Bail {l.name} ({l.tenant_id.name}) expire dans {days} jours',
                'link_model': 're.lease',
                'link_id': l.id,
            })
        # Factures en retard > 15 jours
        late_threshold = today - timedelta(days=15)
        late_invoices = MoveModel.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'in_payment']),
            ('invoice_date_due', '<', late_threshold),
        ])
        for inv in late_invoices[:10]:
            days_late = (today - inv.invoice_date_due).days
            alerts.append({
                'type': 'unpaid',
                'icon': 'fa-money',
                'color': 'red',
                'message': f'Facture {inv.name} ({inv.partner_id.name}) en retard de {days_late} jours',
                'link_model': 'account.move',
                'link_id': inv.id,
            })
        # Pénalités non facturées
        for pen in active_penalties[:5]:
            alerts.append({
                'type': 'penalty',
                'icon': 'fa-exclamation-triangle',
                'color': 'orange',
                'message': f'Pénalité {pen.name} ({pen.lease_id.name}) — {pen.penalty_amount} {pen.currency_id.symbol}',
                'link_model': 're.penalty',
                'link_id': pen.id,
            })

        # --- Paramètre de refresh ---
        refresh_interval = int(self.env['ir.config_parameter'].sudo().get_param(
            're.dashboard.refresh_interval', default='60'
        ))

        return {
            'kpis': {
                'total_properties': total_properties,
                'occupied': occupied,
                'available': available,
                'in_works': in_works,
                'occupation_rate': occupation_rate,
                'lmr_global': lmr_global,
                'unpaid_amount': unpaid_amount,
                'unpaid_count': unpaid_count,
                'penalty_amount': penalty_amount,
                'penalty_count': penalty_count,
                'active_leases_count': len(active_leases),
            },
            'leases': leases_data,
            'services': services_data,
            'alerts': alerts,
            'refresh_interval': refresh_interval,
            'currency_symbol': self.env.company.currency_id.symbol,
        }

    @api.model
    def get_refresh_interval(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            're.dashboard.refresh_interval', default='60'
        ))
