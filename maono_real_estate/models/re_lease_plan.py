# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class ReLeasePlan(models.Model):
    _name = 're.lease.plan'
    _description = 'Plan de périodicité (Abonnement)'
    
    name = fields.Char(string="Nom", required=True)
    billing_period_value = fields.Integer(string="Périodicité", required=True, default=1)
    billing_period_unit = fields.Selection([
        ('week', 'Semaine(s)'),
        ('month', 'Mois'),
        ('year', 'Année(s)')
    ], string="Unité de période", required=True, default='month')
    
    @property
    def billing_period(self):
        if self.billing_period_unit == 'week':
            return relativedelta(weeks=self.billing_period_value)
        elif self.billing_period_unit == 'month':
            return relativedelta(months=self.billing_period_value)
        elif self.billing_period_unit == 'year':
            return relativedelta(years=self.billing_period_value)
        return relativedelta()
    
    billing_first_day = fields.Boolean(string="Aligner au 1er du mois", default=True)
    auto_close_limit = fields.Integer(string="Jours avant clôture auto si impayé", default=30)
    
    invoice_mail_template_id = fields.Many2one('mail.template', string="Template email quittance")
    
    user_closable = fields.Boolean(string="Résiliable sur le portail")
    user_closable_options = fields.Selection([
        ('at_date', 'Á date'),
        ('end_of_period', 'A la fin de la période')
    ], string="Mode de clôture")
    user_extend = fields.Boolean(string="Renouvellement sur le portail")
    user_quantity = fields.Boolean(string="Modification charges sur le portail")
    pausable_by_user = fields.Boolean(string="Pausable sur le portail")
    
    indexation_rate = fields.Float(string="Taux d'indexation annuelle (%)")
    notice_days = fields.Integer(string="Préavis de résiliation (jours)", default=30)

