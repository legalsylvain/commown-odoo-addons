import logging

from collections import OrderedDict

from odoo import models, fields, api

from .common import internal_picking


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "account.analytic.account"

    picking_ids = fields.One2many(
        "stock.picking",
        "contract_id",
        string=u"Pickings")

    quant_ids = fields.One2many(
        "stock.quant",
        string=u"Contract-related stock",
        compute="_compute_quant_ids",
        store=False,
        readonly=True,
    )

    @api.depends("picking_ids")
    def _compute_quant_ids(self):
        for record in self:
            customer_loc = record.partner_id.set_customer_location()
            record.quant_ids = self.env["stock.quant"].search([
                ("history_ids.picking_id.contract_id", "=", record.id),
                ("location_id", "=", customer_loc.id)
            ], order="location_id desc")

    def send_all_picking(self):
        self.ensure_one()

        ref = self.env.ref
        picking_type = ref("stock.picking_type_internal")
        orig_location = ref("commown_devices.stock_location_available_for_rent")

        dest_location = self.partner_id.set_customer_location()

        move_lines = []
        picking_data = {
            "move_type": "direct",
            "picking_type_id": picking_type.id,
            "location_id": orig_location.id,
            "location_dest_id": dest_location.id,
            "origin": self.name,
            "move_lines": move_lines,
        }

        for so_line in self.mapped(
                "recurring_invoice_line_ids.sale_order_line_id"):
            product = so_line.product_id.product_tmpl_id.storable_product_id
            if product and product.tracking == "serial":
                move_lines.append((0, 0, {
                    "name": product.name,
                    "picking_type_id": picking_type.id,
                    "location_id": orig_location.id,
                    "location_dest_id": dest_location.id,
                    "product_id": product.id,
                    "product_uom_qty": so_line.product_uom_qty,
                    "product_uom": so_line.product_uom.id,
                }))

        if not move_lines:
            raise ValueError("No storable product found on contract %s"
                             % self.name)

        picking = self.env["stock.picking"].create(picking_data)
        picking.action_confirm()
        picking.action_assign()
        self.picking_ids |= picking

        return picking

    @api.multi
    def send_device(self, quant, date=None, do_transfer=False):
        """ Create a picking of quant to partner's location.
        If given `date` is falsy (the default), it is set to now.
        If `do_transfer` is True (default: False), execute the picking
        at the previous date.
        """
        dest_location = self.partner_id.set_customer_location()
        return self._create_picking(
            [quant.lot_id], quant.location_id, dest_location, date=date,
            do_transfer=do_transfer)

    @api.multi
    def receive_device(self, lot, dest_location, date=False, do_transfer=False):
        """ Create a picking from partner's location to `dest_location`.
        If given `date` is falsy (the default), it is set to now.
        If `do_transfer` is True (default: False), execute the picking
        at the previous date.
        """

        orig_location = self.partner_id.set_customer_location()
        return self._create_picking([lot], orig_location, dest_location,
                                    date=date, do_transfer=do_transfer)

    def _create_picking(self, lots, orig_location, dest_location,
                        date=None, do_transfer=False):
        self.ensure_one()
        picking = internal_picking(
            self.name, lots, orig_location, dest_location,
            date=date, do_transfer=do_transfer)
        self.picking_ids |= picking
        return picking

    @api.multi
    def stock_at_date(self, date=None):
        "Return the lots at partner's location at the given date"
        self.ensure_one()

        if date is None:
            date = fields.Datetime.now()

        moves = self.env["stock.move"].search([
            ("picking_id.contract_id", "=", self.id),
            ("date", "<=", date),
            ("state", "=", "done"),
        ], order="date ASC")

        lot_ids = OrderedDict()
        partner_loc = self.partner_id.set_customer_location()
        for m in moves:
            for l in m.mapped("lot_ids"):
                lot_ids.setdefault(l.id, 0)
                lot_ids[l.id] += m.location_dest_id == partner_loc and 1 or -1

        return self.env["stock.production.lot"].browse([
            l_id for (l_id, total) in lot_ids.items() if total > 0
        ])
