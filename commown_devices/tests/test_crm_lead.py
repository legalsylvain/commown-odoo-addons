from odoo import fields

from .common import DeviceAsAServiceTC


class CrmLeadTC(DeviceAsAServiceTC):

    def test_picking_confirmation_on_delivery(self):
        "On delivery, picking must be automatically done"

        leads = self.env['crm.lead'].search([
            ('so_line_id.order_id', '=', self.so.id),
        ])
        self.assertEqual(len(leads), 3)
        lead = leads[0]
        lead.send_email_on_delivery = False  # avoid setting-up email
        lot = self.adjust_stock()  # have 1 product in stock
        quant = self.env["stock.quant"].search([("lot_id", "=", lot.id)])

        picking = lead.contract_id.send_device(quant)

        self.assertEqual(picking.mapped('move_lines.product_qty'), [1.])

        picking.pack_operation_ids.pack_lot_ids.do_plus()
        self.assertEqual(picking.state, 'assigned')

        # Set delivery date to trigger the actions and check picking is now done
        lead.delivery_date = fields.Date.today()
        self.assertEqual(picking.state, 'done')