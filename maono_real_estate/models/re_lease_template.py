# -*- coding: utf-8 -*-
from odoo import models, fields

class ReLeaseTemplate(models.Model):
    _name = 're.lease.template'
    _description = 'Modèle de bail'
    
    name = fields.Char(string="Nom du modèle", required=True)
    plan_id = fields.Many2one('re.lease.plan', string="Plan de facturation", required=True)
    
    service_ids = fields.Many2many('re.lease.service', string="Services inclus par défaut")
    
    advance_months = fields.Integer(string="Mois d'avance par défaut", default=0)
    deposit_months = fields.Integer(string="Mois de caution par défaut", default=1)
    
    active = fields.Boolean(default=True)

class ReContractTemplate(models.Model):
    _name = 're.contract.template'
    _description = 'Modèle de contrat de bail'

    name = fields.Char(string="Nom du modèle", required=True)
    lease_type = fields.Selection([
        ('monthly', 'Mensuel'),
        ('annual', 'Annuel'),
        ('commercial', 'Commercial'),
        ('seasonal', 'Saisonnier'),
    ], string="Type de bail applicable")
    body_html = fields.Html(string="Corps du contrat", sanitize=False)
    active = fields.Boolean(default=True)
    note = fields.Text(string="Notes internes")

    def action_test_render(self):
        self.ensure_one()
        from odoo.exceptions import UserError
        lease = self.env['re.lease'].search([('lease_state', 'in', ('1_draft', '3_progress'))], limit=1)
        if not lease:
            raise UserError("Aucun bail (brouillon ou actif) trouvé pour tester le rendu.")
        
        original_template = lease.contract_template_id
        lease.contract_template_id = self
        try:
            rendered_html = lease._render_contract()
        finally:
            lease.contract_template_id = original_template
            
        wizard = self.env['re.contract.test.render.wizard'].create({
            'html_content': rendered_html
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prévisualisation du contrat',
            'res_model': 're.contract.test.render.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

class ReContractTestRenderWizard(models.TransientModel):
    _name = 're.contract.test.render.wizard'
    _description = 'Previsualisation de Rendu de Contrat'
    
    html_content = fields.Html(string="Prévisualisation du Rendu", readonly=True)
