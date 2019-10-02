# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import datetime


class TsmTimePack(models.Model):
    _name = "tsm.time.pack"
    _description = "Packs of time to spent in tasks timesheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start, id desc'

    @api.depends('sale_id')
    def _compute_sale_amount(self):
        # sudo() avoid model security restriction
        sale = self.sudo().sale_id
        currency = (
                self.partner_id.property_product_pricelist.currency_id or
                self.company_currency or
                self.env.user.company_id.currency_id)
        # self.sale_amount = sale.currency_id.compute(
        #                         sale.amount_untaxed, currency)
        self.sale_amount = sale.currency_id._convert(
            sale.amount_untaxed, currency,
            self.company_id, self.date_start or fields.Date.today())

    def _compuete_can_edit(self):
        self.can_edit = self.env.user.has_group('tsm_base.group_tsm_manager')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True, copy=False,
        help="If the active field is set to False, it will allow you to hide"
        " the time pack without removing it.")
    code = fields.Char(string='Time Pack Number',
                       required=True, default="/", readonly=True)
    name = fields.Char(string='Time Pack Title', track_visibility='always',
                       index=True, copy=False)
    description = fields.Html(
        string='Time Pack Description', sanitize=True,
        strip_style=False, translate=False, copy=False,
        help="Details, notes and aclarations about the time pack.")
    timesheet_ids = fields.One2many('tsm.task.timesheet',
                                    'timepack_id', 'Timesheets')
    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              required=True,
                              index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 required=True)
    date_start = fields.Date('Start Date', required=True, copy=False,
                             default=fields.Date.today,
                             help="Start date of the time pack.")
    date_end = fields.Date(string='Ending Date', index=True, copy=False)
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
    ],
        string='Privacy', required=True,
        default='followers',
        help="Holds visibility of the time packs "
             "that belong to the current time pack:\n"
             "- On invitation only: Employees may only "
             "see the followed time packs\n"
             "- Visible by all employees: Employees "
             "may see all time packs\n")
    contrated_hours = fields.Float(
        string='Contrated Hours',
        default=0.0, required=True,
        help='Time contracted by the client for support and it can be '
             'consumed in tasks and timesheet.')
    consumed_hours = fields.Float(compute='_hours_get',
        store=True, string='Hours Consumed',
        help="Computed as: The sum of the timesheet checked "
             "to discount time.")
    remaining_hours = fields.Float(compute='_hours_get',
        readonly=True, store=True,
        string='Remaining Hours',
        help="Computed as: Contrated hours - Consumed hours")
    total_hours_spent = fields.Float(compute='_hours_get',
        store=True, string='Total Hours Spent',
        help="Computed as: Time Spent in tasks.")
    complimentary_hours = fields.Float(compute='_hours_get',
        store=True, string='Complimentary Hours.',
        help="Hours spent but not discounted in time pack.")
    progress = fields.Float(compute='_hours_get',
        store=True, string='Progress', group_operator="avg")
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product')
    description_sale = fields.Text(string='Description Sale')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom_id = fields.Many2one(comodel_name='uom.uom',
                                     string='Unit of Measure')
    price_unit = fields.Float(string='Unit Price', default=0.0, required=True)
    discount = fields.Float(string='Discount (%)',
                    digits=dp.get_precision('Discount'),
                    help='Discount that is applied in generated sale orders.'
                        ' It should be less or equal to 100')
    price_subtotal = fields.Float(compute='_compute_price_subtotal',
                                  digits=dp.get_precision('Account'),
                                  string='Sub Total')
    sale_autoconfirm = fields.Boolean(
                    string='Sale autoconfirm',
                    default=True,
                    help='If it is checked the sale order will be created '
                         'and confirmed automatically',
                    )
    company_currency = fields.Many2one('res.currency',
                            related='company_id.currency_id',
                            readonly=True,
                            help='Utility field to express amount currency')
    sale_id = fields.Many2one(comodel_name='sale.order',
                              copy=False,
                              string='Sale Order',
                              )
    sale_amount = fields.Monetary(compute='_compute_sale_amount',
                                  string='Amount of The Order',
                                  copy=False,
                                  help='Untaxed Total of The Order',
                                  currency_field='company_currency',
                                  )
    can_edit = fields.Boolean(compute='_compuete_can_edit',
                    string='Security: only managers can edit',
                    default=True,
                    help='This field is for security purpose. '
                    'Only members of managers group can modify some fields.')

    _sql_constraints = [
        ('tsm_time_pack_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = \
                self.env['ir.sequence'].next_by_code('tsm.time.pack')
        return super(TsmTimePack, self).create(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('tsm.time.pack')
        return super(TsmTimePack, self).copy(default)

    @api.multi
    def name_get(self):
        result = super(TsmTimePack, self).name_get()
        new_result = []

        for tp in result:
            rec = self.browse(tp[0])
            if tp[1] != 'False':
                name = '[%s] %s' % (rec.code, tp[1])
            else:
                name = '[%s]' % (rec.code)
            new_result.append((rec.id, name))
        return new_result

    def action_view_order(self):
        '''
        This function returns an action that display the order
        given sale order id.
        '''
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_id.id,
            "context": {"create": False, "show_sale": True},
        }

    @api.depends('timesheet_ids.amount', 'timesheet_ids.discount_time',
                 'contrated_hours')
    def _hours_get(self):
        for time in self.sorted(key='id', reverse=True):
            '''use "sudo" here to allow task user (without timesheet 
            user right) to create task'''
            time.total_hours_spent = sum(
                                    time.sudo().timesheet_ids.mapped('amount')
            )
            '''Filter time line checked to discount time'''
            timesheet_consu = time.sudo().mapped('timesheet_ids').filtered(
                     lambda x: x.discount_time)
            time.consumed_hours = sum(timesheet_consu.mapped('amount'))
            time.complimentary_hours = \
                time.total_hours_spent - time.consumed_hours
            time.remaining_hours = time.contrated_hours - time.consumed_hours

            if time.contrated_hours > 0.0:
                time.progress = round(
                    (100.0 * time.consumed_hours) / time.contrated_hours, 2
                )
            else:
                time.progress = 0.0

    @api.multi
    def action_time_pack_send(self):
        self.ensure_one()
        template = self.env.ref(
            'tsm_time_pack.tsm_time_pack_email_template',
            False,
        )
        compose_form = self.env.ref('mail.email_compose_message_wizard_form',
                                    False)
        ctx = dict(
            default_model='tsm.time.pack',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def format_date(self, date):
        # format date following user language
        lang_model = self.env['res.lang']
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.strftime(
            fields.Date.from_string(date), date_format)

    #==========================
    #== Product & Sale Order ==
    #==========================
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        subtotal = self.quantity * self.price_unit
        discount = self.discount / 100
        subtotal *= 1 - discount
        self.price_subtotal = subtotal

    @api.constrains('quantity')
    def _check_quantity(self):
        if not self.quantity > 0.0:
            raise ValidationError(_(
                'Quantity of hours contrated must be greater than 0.'))
        else:
            self.contrated_hours = self.quantity

    @api.constrains('discount')
    def _check_discount(self):
        if self.discount > 100:
            raise ValidationError(_("Discount should be less or equal to 100"))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            vals = {}
            if not self.product_uom_id or (
                    self.product_id.uom_id.category_id.id !=
                    self.product_uom_id.category_id.id):
                vals['product_uom_id'] = self.product_id.uom_id

            partner = self.env.user.partner_id
            product = self.product_id.with_context(
                lang=partner.lang,
                partner=partner.id,
                uom=self.product_uom_id.id
            )

            description_sale = product.name
            if product.description_sale:
                description_sale += '\n' + product.description_sale
            vals['description_sale'] = description_sale

            vals['price_unit'] = product.list_price
            self.update(vals)

    def _prepare_sale_line(self, sale_id):
        sale_line = self.env['sale.order.line'].new({
            'order_id': sale_id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
        })

        '''Get other sale line values from product onchange'''
        sale_line.product_id_change()
        sale_line_vals = sale_line._convert_to_write(sale_line._cache)

        sale_line_vals.update({
            'name': self.description_sale,
            'price_unit': self.price_unit,
            'product_uom_qty': self.quantity,
            'discount': self.discount,
            'tsm_time_pack_id': self.id,
        })

        return sale_line_vals

    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id or not self.product_id:
            raise ValidationError(_("You must first select a Customer "
                                "and product for Time Pack: %s") % self.code)

        currency = (
                self.partner_id.property_product_pricelist.currency_id or
                self.company_currency)

        sale = self.env['sale.order'].new({
            'partner_id': self.partner_id,
            'currency_id': currency.id,
            'date_order': fields.Datetime.today(),
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'origin': self.name_get()[0][1],
            'tsm_time_pack_id': self.id,
        })

        '''Get other sale values from partner onchange'''
        sale.onchange_partner_id()

        return sale._convert_to_write(sale._cache)

    def create_sale(self):
        """
        Create Sale order from Time Pack
        :return: Sele Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()
        sale = self.env['sale.order'].create(sale_vals)

        sale_line_vals = self._prepare_sale_line(sale.id)
        if sale_line_vals:
            self.env['sale.order.line'].create(sale_line_vals)

        '''Update Time Pack with the values from the sale order'''
        vals = {'sale_id': sale.id}
        self.update(vals)

        ''' Autoconfirm sale order if it's checked'''
        if self.sale_autoconfirm:
            sale.action_confirm()

        return sale
