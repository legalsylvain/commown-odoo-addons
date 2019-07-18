from mock import patch

from odoo.models import ValidationError

from odoo.tests.common import at_install, post_install

from odoo.addons.account_invoice_merge_auto.tests.common import \
    MergeInvoicePartnerTC
from odoo.addons.account_invoice_merge_auto_pay.models.res_partner import \
    ResPartner
from odoo.addons.payment.models.payment_acquirer import PaymentTransaction


def fake_do_tx_ok(self, *args, **kwargs):
    self.state = 'done'
    return True


@at_install(False)
@post_install(True)
class ResPartnerAccountingTC(MergeInvoicePartnerTC):

    def setUp(self):
        super(ResPartnerAccountingTC, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        # Maybe the acquirer should be chosen more carefully
        acquirer = self.env['payment.acquirer'].search([
            ('name', '=', 'Ingenico')]).ensure_one()
        self.partner_1.payment_token_id = self.env['payment.token'].create({
            'name': 'test payment token',
            'partner_id': self.partner_1.id,
            'acquirer_id': acquirer.id,
            'acquirer_ref': u'test ref',
        })
        self.partner_1.customer_payment_mode_id = False
        sale_journal = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)
        pmethod = self.env.ref('payment.account_payment_method_electronic_in')
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'customer automatic payment',
            'payment_method_id': pmethod.id,
            'payment_type': 'inbound',
            'bank_account_link': 'fixed',
            'fixed_journal_id': sale_journal.id,
        })

    def test_no_payment_mode(self):
        with self.assertRaises(ValidationError) as err:
            self.create_invoice(self.partner_1, '2019-05-09',
                                # Useless but explicit is better than implicit:
                                payment_mode_id=False)
        self.assertEqual('Payment mode is needed to auto pay an invoice',
                         err.exception.name)

    def _multiple_invoice_merge_test(self, **params):
        params.setdefault('payment_mode_id', self.payment_mode.id)
        inv_1 = self.create_invoice(self.partner_1, '2019-05-09', **params)
        inv_2 = self.create_invoice(self.partner_1, '2019-05-10', **params)

        Partner = self.env['res.partner']
        _invs, merge_infos = Partner._cron_invoice_merge('2019-05-16')
        self.assertEqual(len(merge_infos), 1)
        new_inv = self.env['account.invoice'].browse(merge_infos.keys()[0])
        self.assertEqual(new_inv.date_invoice, '2019-05-16')
        self.assertEqual({inv_1.id, inv_2.id}, set(merge_infos[new_inv.id]))
        self.assertEqual(inv_1.state, 'cancel')
        self.assertEqual(inv_2.state, 'cancel')
        self.assertEqual(self.partner_1.invoice_merge_next_date, '2019-06-15')
        return new_inv

    def test_do_not_pay_refund(self):
        "Do not pay refunds, but do not prevent their merge"
        with patch.object(PaymentTransaction, 's2s_do_transaction') as autopay:
            new_inv = self._multiple_invoice_merge_test(type='out_refund')
        autopay.assert_not_called()
        self.assertEqual(new_inv.state, 'draft')

    def test_auto_pay_merged_invoices(self):
        with patch.object(PaymentTransaction, 's2s_do_transaction',
                          fake_do_tx_ok):
            new_inv = self._multiple_invoice_merge_test()
        self.assertEqual(new_inv.state, 'paid')

    def test_auto_pay_single_invoices(self):
        inv = self.create_invoice(self.partner_1, '2019-05-10',
                                  payment_mode_id=self.payment_mode.id)
        with patch.object(PaymentTransaction, 's2s_do_transaction',
                          fake_do_tx_ok):
            Partner = self.env['res.partner']
            _invs, merge_infos = Partner._cron_invoice_merge('2019-05-16')
        self.assertFalse(merge_infos)
        self.assertEqual(inv.state, 'paid')
        self.assertEqual(inv.date_invoice, '2019-05-10')
        self.assertEqual(self.partner_1.invoice_merge_next_date, '2019-06-15')
