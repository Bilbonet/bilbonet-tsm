# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TsmTimePack(models.Model):
    _name = "tsm.time.pack"
    _description = "Packs of time to spent in tasks timesheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start, id desc'

    @api.depends('sale_id')
    def _compute_sale_amount(self):
        sale = self.sudo().sale_id
        currency = (
                self.partner_id.property_product_pricelist.currency_id or
                self.company_currency or
                self.env.user.company_id.currency_id)
        self.sale_amount = sale.currency_id._convert(
            sale.amount_untaxed, currency,
            self.company_id, self.date_start or fields.Date.today())

    def _compuete_can_edit(self):
        can_edit = self.env.user.has_group('tsm_base.group_tsm_manager')
        for tp in self:
            tp.can_edit = can_edit

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True, copy=False,
        help="If the active field is set to False, it will allow you to hide"
        " the time pack without removing it.")
    code = fields.Char(string='Time Pack Number',
        required=True, default="/", readonly=True)
    name = fields.Char(string='Time Pack Title',
        tracking=20, index=True, copy=False)
    description = fields.Html(string='Time Pack Description', sanitize=True,
        strip_style=False, translate=False, copy=False,
        help="Details, notes and aclarations about the time pack.")
    timesheet_ids = fields.One2many(
        comodel_name='tsm.task.timesheet',
        inverse_name='timepack_id', 
        string='Timesheets', copy=False)
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string='Assigned to',
        default=lambda self: self.env.user, 
        required=True,
        index=True, 
        tracking=30,
    )
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer',
        required=True)
    date_start = fields.Date(string='Start Date', required=True, copy=False,
        default=fields.Date.today,
        help="Start date of the time pack.")
    date_end = fields.Date(string='Ending Date', index=True, copy=False)
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
        ],
        string='Privacy', required=True, default='followers',
        help="Holds visibility of the time packs "
             "that belong to the current time pack:\n"
             "- On invitation only: Employees may only "
             "see the followed time packs\n"
             "- Visible by all employees: Employees "
             "may see all time packs\n")
    contrated_hours = fields.Float(string='Contrated Hours',
        default=0.0, required=True,
        help='Time contracted by the client for support and it can be '
             'consumed in tasks and timesheet.')
    consumed_hours = fields.Float(compute='_hours_get',
        string='Hours Consumed',
        readonly=True, store=True,
        help="Computed as: The sum of the timesheet checked "
             "to discount time.")
    remaining_hours = fields.Float(compute='_hours_get',
        string='Remaining Hours',
        readonly=True, store=True,
        help="Computed as: Contrated hours - Consumed hours")
    total_hours_spent = fields.Float(compute='_hours_get',
        string='Total Hours Spent',
        readonly=True, store=True,
        help="Computed as: Time Spent in tasks.")
    complimentary_hours = fields.Float(compute='_hours_get',
        string='Complimentary Hours.',
        readonly=True, store=True,
        help="Hours spent but not discounted in time pack.")
    progress = fields.Float(compute='_hours_get',
        string='Progress',
        readonly=True, store=True,
        group_operator="avg")
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    description_sale = fields.Text(string='Description Sale')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom_id = fields.Many2one(comodel_name='uom.uom',
        string='Unit of Measure')
    price_unit = fields.Float(
        string='Unit Price', default=0.0, required=True)
    discount = fields.Float(
        string='Discount (%)',
        digits="Discount",
        help='Discount that is applied in generated sale orders.'
             ' It should be less or equal to 100')
    price_subtotal = fields.Float(
        compute='_compute_price_subtotal',
        string='Sub Total', 
        digits=0)
    sale_autoconfirm = fields.Boolean(
        string='Sale autoconfirm', default=True,
        help='If it is checked the sale order will be created '
             'and confirmed automatically',)
    company_currency = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string="Company Currency", readonly=True,
        help='Utility field to express amount currency')
    sale_id = fields.Many2one(
        comodel_name='sale.order', 
        string='Sale Order', copy=False)
    sale_amount = fields.Monetary(
        compute='_compute_sale_amount',
        string='Amount of The Order',
        currency_field='company_currency', copy=False,
        help='Untaxed Total of The Order',)
    can_edit = fields.Boolean(
        compute='_compuete_can_edit',
        string='Security: only managers can edit', default=True,
        help='This field is for security purpose. '
             'Only members of managers group can modify some fields.')

    _sql_constraints = [
        ('tsm_time_pack_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.depends(
        'contrated_hours',
        'timesheet_ids',
        'timesheet_ids.amount', 
        'timesheet_ids.discount_time',
    )
    def _hours_get(self):
        for time in self.sorted(key='id', reverse=True):
            '''
            use "sudo" here to allow user (without timesheet user right) 
            to access timesheets
            '''

            '''Filter timesheet ids checked to discount time'''
            timesheet_consu_ids = time.sudo().mapped('timesheet_ids').filtered(
                lambda x: x.discount_time
            )

            total_hours_spent = sum(time.sudo().timesheet_ids.mapped('amount'))
            consumed_hours = sum(timesheet_consu_ids.mapped('amount'))
            complimentary_hours = total_hours_spent - consumed_hours
            remaining_hours = time.contrated_hours - consumed_hours
            if time.contrated_hours > 0.0:
                progress = round(
                    (100.0 * consumed_hours) / time.contrated_hours, 2
                )
            else:
                progress = 0.0

            time.update({
                'total_hours_spent': total_hours_spent,
                'consumed_hours':  consumed_hours,
                'complimentary_hours': complimentary_hours,
                'remaining_hours': remaining_hours,
                'progress': progress,
            })

            if progress >= 90:
                #TODO: Improve the way to express hours in format "%H:%M"
                cont_hours = str(datetime.timedelta(hours=time.contrated_hours))[:5]
                consu_hours = str(datetime.timedelta(hours=consumed_hours))[:5]
                txt_msg = _(
                    '<h6>Contrated Hours: %s</h6>'
                    '<h6>Consumed Hours: %s</h6>'
                    '<h4 class="text-danger">Progress: %s %%</h4>'
                ) % (
                    cont_hours, 
                    consu_hours, 
                    progress
                )
                title_msg=_('Time Pack %s Warning!!') % (time.code)
                user_msg = {
                    "message": txt_msg,
                    "title":  title_msg,
                    "sticky": False,
                    "html": True,
                }
                self.env.user.notify_danger(**user_msg)

    def action_time_pack_send(self):
        '''
        This function opens a window to compose an email,
        with the time pack template message loaded by default
        '''
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('tsm_time_pack.tsm_time_pack_email_template', raise_if_not_found=False)
        if mail_template and mail_template.lang:
            lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'tsm.time.pack',
            'default_res_id': self.id,
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
            'model_description': 'TSM Time Pack',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    # -------------------------
    #== Product & Sale Order ==
    # -------------------------
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

    def _prepare_sale_line(self):
        self.ensure_one()
        name = (
            _(
                '{description_sale}\n Time Pack: [{code}] {name}' 
            ).format(
                description_sale = self.description_sale,
                code = self.code,
                name = self.name or ''
            )
        )

        sale_line_vals = {
            'product_id': self.product_id.id,
            'name': name,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.quantity,
            'price_unit': self.price_unit,
            'discount': self.discount,
        }
        sale_line = self.env['sale.order.line'].new(sale_line_vals)
        return sale_line._convert_to_write(sale_line._cache)

    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id or not self.product_id:
            raise ValidationError(_(
                "You must first select a Customer and a Product for\n"
                "Time Pack: %s"
            ) % self.code)

        client_ref = (
            _(
                'Time Pack: [{code}] {name}' 
            ).format(
                code = self.code,
                name = self.name or ''
            )
        )

        sale = self.env['sale.order'].new(
            {
                'partner_id': self.partner_id,
                'date_order': fields.Date.to_string(date.today()),
                'origin': self.code,
                'client_order_ref': client_ref,
                'company_id': self.company_id.id,
                'user_id': self.user_id.id,
            }
        )

        if self.partner_id.property_payment_term_id:
            sale.payment_term_id = self.partner_id.property_payment_term_id
        if self.partner_id.property_account_position_id:
            sale.fiscal_position_id = self.partner_id.property_account_position_id
        if self.partner_id.property_product_pricelist.id:
            sale.pricelist_id = self.partner_id.property_product_pricelist.id

        return sale._convert_to_write(sale._cache)

    def create_sale(self):
        """
        Create Sale order from Time Pack
        :return: Sele Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()

        sale_vals.setdefault('order_line', [])
        sale_line_vals = self._prepare_sale_line()
        if sale_line_vals:
            sale_vals['order_line'].append(
                (0, 0, sale_line_vals)
            )
        sale = self.env['sale.order'].create(sale_vals)
        sale.message_post_with_view('mail.message_origin_link',
            values={'self': sale, 'origin': self},
            subtype_id=self.env.ref('mail.mt_note').id)
        
        # Update Time Pack with the values from the sale order
        vals = {'sale_id': sale.id}
        self.update(vals)

        # Autoconfirm sale order if it's checked
        if self.sale_autoconfirm:
            sale.action_confirm()

        return sale

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

    # ------------------
    # CRUD overrides
    # ------------------
    @api.model_create_multi
    def create(self, vals_list):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)
        # Assign new code
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                                                            'tsm.time.pack')

        return super(TsmTimePack, self.with_context(context)).create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['code'] = self.env['ir.sequence'].next_by_code('tsm.time.pack')
        return super().copy(default)

    def name_get(self):
        """Get the proper display name formatted as 'code, name'."""
        result = []
        for rec in self:
            name = '[%s]' % (rec.code)
            if rec.name:
                name = '[%s] %s' % (rec.code, rec.name)
            result.append((rec.id, name))
        return result
