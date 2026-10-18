# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TsmTaskMaterial(models.Model):
    _name = "tsm.task.material"
    _description = "TSM Task Material Used"
    _order = "sequence,id"
    _check_company_auto = True

    task_id = fields.Many2one(
        comodel_name="tsm.task", string="Task", ondelete="cascade", required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        check_company=True,
    )
    company_id = fields.Many2one(related="task_id.company_id")
    name = fields.Text(
        string="Description",
        compute="_compute_name",
        store=True,
        readonly=False,
        precompute=True,
    )
    quantity = fields.Float(
        default=1.0, required=True, digits="Product Unit of Measure"
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
        precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    price_unit = fields.Float(
        string="Unit Price",
        compute="_compute_price_unit",
        store=True,
        readonly=False,
        precompute=True,
        required=True,
        digits="Product Price",
    )
    price_subtotal = fields.Float(
        compute="_compute_price_subtotal", string="Sub Total", digits="Account"
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        help="Discount that is applied in generated sale orders."
        " It should be less or equal to 100",
    )
    sequence = fields.Integer(
        default=10,
        help="Sequence of the line in the list of materials",
    )
    company_currency = fields.Many2one(
        "res.currency",
        related="task_id.company_id.currency_id",
        readonly=True,
        help="Utility field to express amount currency",
    )

    @api.depends("quantity", "price_unit", "discount")
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            line.price_subtotal = subtotal

    @api.constrains("quantity")
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    self.env._("Quantity of material consumed must be greater than 0.")
                )

    @api.constrains("discount")
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    self.env._("Discount should be less or equal to 100")
                )

    @api.depends("product_id", "task_id.partner_id.lang")
    def _compute_name(self):
        for line in self:
            product = line.product_id.with_context(
                lang=line.task_id.partner_id.lang or self.env.lang,
            )
            line.name = (
                product.get_product_multiline_description_sale() if product else False
            )

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        for line in self:
            if not line.product_id:
                line.product_uom_id = False
            elif (
                not line.product_uom_id
                or line.product_uom_id.category_id != line.product_id.uom_id.category_id
            ):
                line.product_uom_id = line.product_id.uom_id

    @api.depends("product_id", "product_uom_id")
    def _compute_price_unit(self):
        for line in self:
            product = line.product_id.with_context(uom=False)
            line.price_unit = (
                product.uom_id._compute_price(product.lst_price, line.product_uom_id)
                if product
                else 0.0
            )

    @api.constrains("product_id", "product_uom_id")
    def _check_product_uom_id(self):
        for line in self:
            if line.product_uom_id and (
                line.product_uom_id.category_id != line.product_id.uom_id.category_id
            ):
                raise ValidationError(
                    self.env._(
                        "The unit of measure must belong to the product's category."
                    )
                )

    def _check_task_editable(self):
        tasks = self.task_id
        tasks.check_access("write")
        if any(tasks.mapped("sale_id")):
            raise UserError(
                self.env._(
                    "Materials cannot be changed once the task has a sale order."
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        materials = super().create(vals_list)
        materials._check_task_editable()
        return materials

    def write(self, vals):
        self.check_access("write")
        self._check_task_editable()
        if vals.get("task_id"):
            self.env["tsm.task"].browse(vals["task_id"]).check_access("write")
        result = super().write(vals)
        self._check_task_editable()
        return result

    @api.ondelete(at_uninstall=False)
    def _unlink_except_sale_order(self):
        self._check_task_editable()

    def _prepare_sale_line(self, sale=None):
        self.ensure_one()
        company = self.task_id.company_id or self.env.company
        price_unit = self.price_unit
        if sale:
            price_unit = company.currency_id._convert(
                price_unit,
                sale.currency_id,
                company,
                fields.Date.to_date(sale.date_order),
                round=False,
            )
        return {
            "sequence": self.sequence,
            "product_id": self.product_id.id,
            "name": self.name
            or self.product_id.get_product_multiline_description_sale(),
            "product_uom": (self.product_uom_id or self.product_id.uom_id).id,
            "price_unit": price_unit,
            "product_uom_qty": self.quantity,
            "discount": self.discount,
        }
