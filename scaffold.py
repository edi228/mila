import os

base_path = '/Users/edouard/Documents/Antigravity/immo/maono_real_estate'

wizards_py = {
    '__init__.py': '''from . import re_lease_renew_wizard
from . import re_lease_close_wizard
from . import re_penalty_compute_wizard
from . import re_saving_transfer_wizard
''',
    're_lease_renew_wizard.py': '''# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseRenewWizard(models.TransientModel):
    _name = 're.lease.renew.wizard'
    _description = 'Wizard de Renouvellement'

    lease_id = fields.Many2one('re.lease', string="Bail actuel")
    new_start_date = fields.Date(string="Nouvelle date de début")
    
    def action_renew(self):
        pass
''',
    're_lease_close_wizard.py': '''# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseCloseWizard(models.TransientModel):
    _name = 're.lease.close.wizard'
    _description = 'Wizard de Clôture'

    lease_id = fields.Many2one('re.lease', string="Bail à clôturer")
    close_reason_id = fields.Many2one('re.lease.close.reason', string="Motif")
    close_date = fields.Date(string="Date de résiliation")
    
    def action_close(self):
        pass
''',
    're_penalty_compute_wizard.py': '''# -*- coding: utf-8 -*-
from odoo import models, fields

class RePenaltyComputeWizard(models.TransientModel):
    _name = 're.penalty.compute.wizard'
    _description = 'Wizard Calcul Pénalités'

    def action_compute(self):
        pass
''',
    're_saving_transfer_wizard.py': '''# -*- coding: utf-8 -*-
from odoo import models, fields

class ReSavingTransferWizard(models.TransientModel):
    _name = 're.saving.transfer.wizard'
    _description = 'Transférer l\'épargne'

    move_id = fields.Many2one('account.move', string="Facture Orignale")
    source_account_id = fields.Many2one('account.account', string="Compte Source")
    target_account_id = fields.Many2one('account.account', string="Compte Cible")
    journal_id = fields.Many2one('account.journal', string="Journal")
    total_saving_amount = fields.Monetary(string="Total à transférer")
    currency_id = fields.Many2one('res.currency')
    
    def action_transfer(self):
        pass
'''
}

wizards_xml = {
    're_lease_renew_wizard_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_close_wizard_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_penalty_compute_wizard_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_saving_transfer_wizard_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>'
}

data_xml = {
    're_lease_plan_data.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_close_reason_data.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_account_tax_data.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_service_data.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    'ir_sequence_tenant_ref.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    'mail_template_data.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>'
}

report_xml = {
    're_lease_contract_report.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_quittance_report.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    '__init__.py': 'from . import re_lease_log_report\n',
    're_lease_log_report.py': '# -*- coding: utf-8 -*-\nfrom odoo import models\n\nclass ReLeaseLogReport(models.AbstractModel):\n    _name = "report.re_lease_log"\n'
}

views_xml = {
    're_lease_plan_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_account_tax_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_building_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_property_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_property_service_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_template_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_tax_line_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_saving_rule_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_penalty_schedule_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_identity_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_log_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_penalty_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    'res_partner_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    're_lease_views.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
    'menus.xml': '<?xml version="1.0" encoding="utf-8"?><odoo></odoo>',
}

controllers_py = {
    '__init__.py': 'from . import portal\n',
    'portal.py': '''# -*- coding: utf-8 -*-
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class CustomerPortalReLease(CustomerPortal):
    pass
'''
}

def write_files(target_dir, content_dict):
    os.makedirs(target_dir, exist_ok=True)
    for filename, content in content_dict.items():
        with open(os.path.join(target_dir, filename), 'w') as f:
            f.write(content)

write_files(os.path.join(base_path, 'wizard'), wizards_py)
write_files(os.path.join(base_path, 'wizard'), wizards_xml)
write_files(os.path.join(base_path, 'data'), data_xml)
write_files(os.path.join(base_path, 'report'), report_xml)
write_files(os.path.join(base_path, 'views'), views_xml)
write_files(os.path.join(base_path, 'controllers'), controllers_py)

print("Scaffold complete.")
