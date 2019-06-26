from odoo import fields, models


class AccountAnalyticContract(models.Model):
    _inherit = 'account.analytic.contract'

    transaction_label = fields.Text(
        string='Payment label', required=True, default='#INV#',
        help=('Label to be used for the bank payment. '
              'Possible markers: #START#, #END#, #INV# (invoice number)'),
    )