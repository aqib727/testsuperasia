# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.tools.translate import _
from odoo.tools.misc import format_date, formatLang, get_lang
from json import loads
import json
import datetime

class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_report_name(self):
        """
        Override
        Return the name of the report
        """
        return _('Statement')

    def _get_columns_name(self, options):
        headers = super(AccountFollowupReport, self)._get_columns_name(options)

        headers = headers[:3] + headers[5:]
        headers[1]['name'] = _('Invoice Date')
        del headers[-1]
        headers.append({'name': _('Amount'), 'class': 'number o_price_total', 'style': 'text-align:right; white-space:nowrap;'})
        headers.append({'name': _('Balance'), 'class': 'number o_price_total', 'style': 'text-align:right; white-space:nowrap;'})
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.company):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            balance = 0
            for aml in aml_recs:
                amount = -aml.credit or aml.debit or aml.amount_residual_currency or 0
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                balance += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment or aml.credit:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date', 'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = self._format_aml_name(aml.name, aml.move_id.ref, aml.move_id.name)
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                balance_total = formatLang(self.env, balance, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env, aml.expected_pay_date, lang_code=lang_code) if aml.expected_pay_date else ''
                columns = [
                    format_date(self.env, aml.date, lang_code=lang_code),
                    date_due,
                    (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
                    {'name': '', 'blocked': aml.blocked},
                    amount,
                    balance_total,
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:2] + columns[4:]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })

                if aml.matched_credit_ids:
                    for credit in aml.matched_credit_ids:
                        amount = credit.amount
                        date_due = format_date(self.env, credit.credit_move_id.date, lang_code=lang_code)
                        total -= amount or 0
                        total_issued -= amount or 0
                        balance -= amount or 0
                        move_line_name = self._format_aml_name(aml.name, aml.move_id.ref, aml.move_id.name)
                        if self.env.context.get('print_mode'):
                            move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                        amount = formatLang(self.env, amount, currency_obj=currency)
                        balance_total = formatLang(self.env, balance, currency_obj=currency)
                        line_num += 1
                        columns = [
                            '',
                            date_due,
                            '',
                            {'name': '', 'blocked': aml.blocked},
                            amount,
                            balance_total,
                        ]
                        if self.env.context.get('print_mode'):
                            columns = columns[:2] + columns[4:]
                        try:
                            credit_name = credit.credit_move_id.name.split(' ', 1)[1]
                        except:
                            credit_name = 'Payment'
                        lines.append({
                            'id': aml.id,
                            'account_move': aml.move_id,
                            'name': credit_name,
                            'caret_options': 'followup',
                            'style': 'color: red',
                            'move_id': credit.credit_move_id.id,
                            'type': is_payment and 'payment' or 'unreconciled_aml',
                            'unfoldable': False,
                            'columns': [type(v) == dict and v or {'name': v} for v in columns],
                        })
                        
                
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': [{'name': v} for v in [''] * (1 if self.env.context.get('print_mode') else 3) + [total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 3,
                    'columns': [{'name': v} for v in [''] * (1 if self.env.context.get('print_mode') else 3) + [_('Total Overdue'), total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'style': 'border-bottom-style: none',
                'unfoldable': False,
                'level': 0,
                'columns': [{} for col in columns],
            })
        # Remove the last empty line
        if lines:
            lines.pop()
        return lines

    def get_new_lines(self, options, line_id=None):
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        res = {}
        today = fields.Date.today()
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.company):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            days_0_29 = 0
            days_30_39 = 0
            days_40_49 = 0
            days_50_59 = 0
            days_60_plus = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual  
                date_due = aml.date_maturity or aml.date
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                if is_overdue or aml.credit:
                    days_overdue = today - date_due
                    if days_overdue <= datetime.timedelta(days = 29):
                        days_0_29 += amount
                    elif days_overdue <= datetime.timedelta(days = 39):
                        days_30_39 += amount
                    elif days_overdue <= datetime.timedelta(days = 49):
                        days_40_49 += amount
                    elif days_overdue <= datetime.timedelta(days = 59):
                        days_50_59 += amount
                    else:
                        days_60_plus += amount
            days_0_29 = formatLang(self.env, days_0_29, currency_obj=currency)
            days_30_39 = formatLang(self.env, days_30_39, currency_obj=currency)
            days_40_49 = formatLang(self.env, days_40_49, currency_obj=currency)
            days_50_59 = formatLang(self.env, days_50_59, currency_obj=currency)
            days_60_plus = formatLang(self.env, days_60_plus, currency_obj=currency)
            line = {
                'values': [days_0_29, days_30_39, days_40_49, days_50_59, days_60_plus],
                'columns': ['0 - 29', '30 - 39', '40 - 49', '50 - 59', '60+'],
                }
            return line

    def get_html(self, options, line_id=None, additional_context={}):
        
        additional_context['outstanding_line'] = self.get_new_lines(options)
        return super(AccountFollowupReport, self).get_html(options, line_id=line_id, additional_context=additional_context)