# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

def number_to_french_words(number):
    units = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    tens = ["", "dix", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    teens = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
    
    if number == 0:
        return "zéro"
        
    def convert_below_thousand(n):
        if n == 0:
            return ""
        res = []
        c = n // 100
        d = (n % 100) // 10
        u = n % 10
        
        if c > 0:
            if c == 1:
                res.append("cent")
            else:
                res.append(units[c] + " cent")
        
        if d == 1:
            res.append(teens[u])
        elif d == 7:
            res.append("soixante-" + teens[u])
        elif d == 9:
            res.append("quatre-vingt-" + teens[u])
        elif d > 0:
            if u == 1 and d != 8:
                res.append(tens[d] + " et un")
            else:
                val = tens[d] + ("-" + units[u] if u > 0 else "")
                res.append(val)
        elif u > 0:
            res.append(units[u])
            
        return " ".join(res).strip()

    parts = []
    billions = number // 1000000000
    millions = (number % 1000000000) // 1000000
    thousands = (number % 1000000) // 1000
    rest = number % 1000
    
    if billions > 0:
        parts.append(convert_below_thousand(billions) + (" milliard" + ("s" if billions > 1 else "")))
    if millions > 0:
        parts.append(convert_below_thousand(millions) + (" million" + ("s" if millions > 1 else "")))
    if thousands > 0:
        if thousands == 1:
            parts.append("mille")
        else:
            parts.append(convert_below_thousand(thousands) + " mille")
    if rest > 0:
        parts.append(convert_below_thousand(rest))
        
    res = " ".join(parts).strip()
    return res.replace(" cent s", " cents").replace(" vingt s", " vingts")

class AccountMove(models.Model):
    _inherit = 'account.move'

    lease_id = fields.Many2one('re.lease', string="Bail lié")
    invoice_period_start = fields.Date(string="Début de période")
    invoice_period_end = fields.Date(string="Fin de période")
    is_entry_invoice = fields.Boolean(string="Est le reçu d'entrée (caution & avance)", default=False)
    
    amount_in_words = fields.Char(string="Montant en lettres", compute='_compute_amount_in_words')

    lease_saving_ids = fields.One2many('account.move.saving.line', 'move_id', string="Lignes d'épargne calculées")
    total_saving_amount = fields.Monetary(string="Total épargne à provisionner", compute='_compute_total_saving_amount')
    saving_transferred = fields.Boolean(string="Épargne transférée", default=False)
    saving_transfer_date = fields.Date(string="Date du transfert")
    saving_transfer_move_id = fields.Many2one('account.move', string="Écriture de transfert")

    @api.depends('amount_total')
    def _compute_amount_in_words(self):
        for move in self:
            move.amount_in_words = move.amount_to_words(move.amount_total)

    def amount_to_words(self, amount):
        try:
            val = int(round(amount))
            return number_to_french_words(val).upper() + " FRANCS CFA"
        except Exception:
            return ""

    @api.depends('lease_saving_ids.saving_amount')
    def _compute_total_saving_amount(self):
        for move in self:
            move.total_saving_amount = sum(move.lease_saving_ids.mapped('saving_amount'))

    def action_print_payment_receipt(self):
        self.ensure_one()
        from odoo.exceptions import UserError
        payments = self.payment_ids or self.matched_payment_ids
        if not payments:
            reconciled_lines = self.line_ids.filtered(lambda l: l.reconciled)
            payments = reconciled_lines.mapped('matched_debit_ids.debit_move_id.payment_id') | \
                       reconciled_lines.mapped('matched_credit_ids.credit_move_id.payment_id')
        if not payments:
            payments = self.env['account.payment'].search([
                ('reconciled_invoice_ids', 'in', self.ids)
            ])
        if not payments:
            raise UserError(_("Aucun paiement enregistré pour cette échéance. Veuillez d'abord enregistrer le paiement."))
        return self.env.ref('maono_real_estate.report_re_payment_receipt').report_action(payments[0])

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    lease_id = fields.Many2one('re.lease', string="Bail lié", compute='_compute_lease_id', store=True)
    period_start = fields.Date(string="Début de période", compute='_compute_period')
    period_end = fields.Date(string="Fin de période", compute='_compute_period')
    amount_in_words = fields.Char(string="Montant en lettres", compute='_compute_amount_in_words')

    @api.depends('reconciled_invoice_ids')
    def _compute_lease_id(self):
        for pay in self:
            invoices = pay.reconciled_invoice_ids
            leases = invoices.mapped('lease_id')
            pay.lease_id = leases[0].id if leases else False

    @api.depends('reconciled_invoice_ids')
    def _compute_period(self):
        for pay in self:
            invoices = pay.reconciled_invoice_ids
            valid_start = [i.invoice_period_start for i in invoices if i.invoice_period_start]
            valid_end = [i.invoice_period_end for i in invoices if i.invoice_period_end]
            pay.period_start = min(valid_start) if valid_start else False
            pay.period_end = max(valid_end) if valid_end else False

    @api.depends('amount')
    def _compute_amount_in_words(self):
        for pay in self:
            pay.amount_in_words = pay.amount_to_words(pay.amount)

    def amount_to_words(self, amount):
        try:
            val = int(round(amount))
            return number_to_french_words(val).upper() + " FRANCS CFA"
        except Exception:
            return ""

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for payment in self:
            if payment.payment_type == 'inbound' and payment.lease_id:
                payment._generate_savings_entry()
        return res

    def _generate_savings_entry(self):
        self.ensure_one()
        lease = self.lease_id
        active_rules = lease.saving_rule_ids.filtered('is_active')
        if not active_rules:
            return
            
        misc_journal = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        if not misc_journal:
            return
            
        rent_product = self.env['product.product'].search([('is_rental_service', '=', True)], limit=1)
        income_account = rent_product.property_account_income_id or rent_product.categ_id.property_account_income_categ_id
        if not income_account:
            income_account = self.env['account.account'].search([
                ('account_type', '=', 'income'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        if not income_account:
            return
            
        for rule in active_rules:
            base = lease.rent_amount if rule.base == 'rent' else self.amount
            if rule.mode == 'percent':
                amount = base * (rule.value / 100.0)
            else:
                amount = rule.value
                
            if amount <= 0:
                continue
                
            credit_account = rule.target_account_id
            if not credit_account:
                continue
                
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'journal_id': misc_journal.id,
                'date': fields.Date.context_today(self),
                'ref': _("Provision Épargne — %s — Bail %s") % (rule.name, lease.name),
                'lease_id': lease.id,
                'line_ids': [
                    (0, 0, {
                        'name': _("Débit Loyer pour Épargne %s") % rule.name,
                        'account_id': income_account.id,
                        'debit': amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'name': _("Provision Épargne %s") % rule.name,
                        'account_id': credit_account.id,
                        'debit': 0.0,
                        'credit': amount,
                    }),
                ]
            })
            move.action_post()
            
            invoice = self.reconciled_invoice_ids[0] if self.reconciled_invoice_ids else False
            if invoice:
                self.env['account.move.saving.line'].create({
                    'move_id': invoice.id,
                    'saving_rule_id': rule.id,
                    'base_amount': base,
                })

class AccountMoveSavingLine(models.Model):
    _name = 'account.move.saving.line'
    _description = "Ligne d'épargne calculée"

    move_id = fields.Many2one('account.move', string="Facture parente", required=True, ondelete='cascade')
    saving_rule_id = fields.Many2one('re.lease.saving.rule', string="Règle appliquée", required=True)
    name = fields.Char(related='saving_rule_id.name', string="Motif")
    
    base_amount = fields.Monetary(string="Base de calcul", currency_field='currency_id')
    saving_amount = fields.Monetary(string="Montant d'épargne", compute='_compute_saving_amount', currency_field='currency_id')
    
    target_account_id = fields.Many2one('account.account', related='saving_rule_id.target_account_id')
    currency_id = fields.Many2one('res.currency', related='move_id.currency_id')
    lease_id = fields.Many2one('re.lease', related='saving_rule_id.lease_id', string="Bail", store=True)

    @api.depends('saving_rule_id', 'base_amount')
    def _compute_saving_amount(self):
        for line in self:
            if line.saving_rule_id:
                if line.saving_rule_id.mode == 'percent':
                    line.saving_amount = line.base_amount * (line.saving_rule_id.value / 100.0)
                else:
                    line.saving_amount = line.saving_rule_id.value
            else:
                line.saving_amount = 0.0
