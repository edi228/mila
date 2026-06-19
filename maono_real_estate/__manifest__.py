# -*- coding: utf-8 -*-
{
    'name': 'Module de Gestion Immobilière',
    'version': '3.3',
    'category': 'Real Estate',
    'summary': 'Gestion immobilière locative complète : patrimoine, baux, quittances, interventions, taxes, pénalités, épargne, dashboard OWL.',
    'description': """
Module de Gestion Immobilière — Odoo 19
=======================================
Auteur : AFRO IT | Version 3.3
    """,
    'author': 'AFRO IT',
    'depends': ['sale', 'account', 'mail', 'payment', 'portal', 'rating'],
    'data': [
        # Sécurité
        'security/re_security.xml',
        'security/ir.model.access.csv',
        # Données de configuration
        'data/re_lease_plan_data.xml',
        'data/re_lease_close_reason_data.xml',
        'data/re_account_tax_data.xml',
        'data/re_lease_service_data.xml',
        'data/re_product_data.xml',
        'data/ir_sequence_tenant_ref.xml',
        'data/mail_template_data.xml',
        'data/re_lease_cron.xml',
        'data/re_dashboard_data.xml',
        # Vues — ordre important (actions avant menus)
        'views/re_lease_plan_views.xml',
        'views/re_account_tax_views.xml',
        'views/re_lease_views.xml',
        'views/re_property_views.xml',
        'views/re_building_views.xml',
        'views/re_property_service_views.xml',
        'views/re_lease_template_views.xml',
        'views/re_lease_tax_line_views.xml',
        'views/re_lease_saving_rule_views.xml',
        'views/re_lease_penalty_schedule_views.xml',
        'views/re_lease_identity_views.xml',
        'views/re_lease_log_views.xml',
        'views/re_penalty_views.xml',
        'views/res_partner_views.xml',
        # Wizards
        'wizard/re_lease_renew_wizard_views.xml',
        'wizard/re_lease_close_wizard_views.xml',
        'wizard/re_penalty_compute_wizard_views.xml',
        'wizard/re_saving_transfer_wizard_views.xml',
        'wizard/re_lease_amendment_wizard_views.xml',
        # Rapports
        'report/re_lease_contract_report.xml',
        'report/re_lease_quittance_report.xml',
        # Menus (en dernier car référencent toutes les actions)
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'maono_real_estate/static/src/dashboard/immo_dashboard.js',
            'maono_real_estate/static/src/dashboard/immo_dashboard.xml',
            'maono_real_estate/static/src/dashboard/immo_dashboard.scss',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'OPL-1',
}
