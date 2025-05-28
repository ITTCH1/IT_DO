from odoo import models , fields, api ,Command, _
from odoo.exceptions import ValidationError
class DoflexTicket(models.Model):
    _name = 'docflex.ticket'
    # _inherit="helpdesk.ticket"
    _inherit = [
        'portal.mixin',
        'mail.thread.cc',
        'utm.mixin',
        'rating.mixin',
        'mail.activity.mixin',
        'mail.tracking.duration.mixin',
    ]
    
  
    _description = 'المذكرات'
    _track_duration_field = 'stage_id'
    _sql_constraints = [
    ('number_unique', 'UNIQUE(number)', 'الرقم التسلسلي يجب أن يكون فريدًا!'),
]
    
    name = fields.Char(string='الموضوع', required=True, index=True, tracking=True)

    number = fields.Char(
        string='الرقم التسلسلي',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False
    )
    referrenc_number=fields.Char("رقم المرجع ")
    topic=fields.Text("البيان")
    note=fields.Text("الملاحظة")
    partner_number=fields.Char("رقم الجهة")
    ticket_date = fields.Datetime(
        string='تاريخ المذكرة',
        default=fields.Datetime.now,
    )
    partner_from_id = fields.Many2one(
        string='من الجهة',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    partner_to_id = fields.Many2one(
        string='الى الجهة',
        comodel_name='res.partner',
        ondelete='restrict',
    )
    folder_id= fields.Many2one(
        string='مساحة العمل',
        comodel_name='documents.folder',
        ondelete='restrict',
    )

    
    ticket_section_id = fields.Many2one(
        'ticket.section',
        string='قسم المذكرة',
        ondelete='restrict',
    )
    ticket_priority_id = fields.Many2one(
        string='درجة الاولوية ',
        comodel_name='ticket.priority',
        ondelete='restrict',
    )
    ticket_security_id = fields.Many2one(
        string='درجة السرية',
        comodel_name='ticket.security',
        ondelete='restrict',
    )
    ticket_type = fields.Many2one('ticket.type', string="Ticket Type", 
                                default=lambda self: self._get_default_ticket_type())
    ticket_status_id = fields.Many2one(
        string='حالة المذكرة',
        comodel_name='ticket.status',
        ondelete='restrict',
    )
    ticket_summary_id = fields.Many2one(
        string='الموجز',
        comodel_name='ticket.summary',
        ondelete='restrict',
    )
    
    ticket_classification_id = fields.Many2one(
        string='تصنيف المذكرة ',
        comodel_name='ticket.classification',
        ondelete='restrict',
    )
    stage_id = fields.Many2one(
        'docflex.ticket.stage', string='المرحلة',
          store=True,
        readonly=False, ondelete='restrict',
        tracking=1,
        copy=False, index=True
    )
    fold = fields.Boolean(related="stage_id.fold")
    wait_archive = fields.Boolean(
        string='wait archive',
    )
    
    archive = fields.Boolean(
        string='archive',
    )
    active = fields.Boolean(default=True)
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_user_ids')
    is_partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_is_partner_email_update')
    is_partner_phone_update = fields.Boolean('Partner Phone will Update', compute='_compute_is_partner_phone_update')
    partner_name = fields.Char(string='Customer Name', compute='_compute_partner_name', store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_partner_email', inverse="_inverse_partner_email", store=True, readonly=False)
    partner_phone = fields.Char(string='Customer Phone', compute='_compute_partner_phone', inverse="_inverse_partner_phone", store=True, readonly=False)
    commercial_partner_from_id = fields.Many2one(related="partner_from_id.commercial_partner_id")
    closed_by_partner = fields.Boolean('Closed by Partner', readonly=True)
    tag_ids = fields.Many2many('docflex.tag', string='Tags')
    company_id = fields.Many2one( string='Company',comodel_name='res.company', store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Created by User', readonly=True)
    user_name = fields.Char(string="User Name", readonly=True)
    department_id = fields.Many2one('hr.department', string='User Department', readonly=True)
    color = fields.Integer(string='Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    
    ticket_type_code = fields.Char(related='ticket_type.code', store=True)
    ticket_section_code = fields.Selection(related='ticket_section_id.code', store=True)
    sequence_year = fields.Char(compute='_compute_sequence_year', store=True)

    # إضافة هذه الحقول في نموذج docflex.ticket
    ticket_date_date = fields.Date(
        string="تاريخ المذكرة (تاريخ فقط)",
        compute='_compute_ticket_date_date',
        store=True,
        index=True
    )

    sequence_year = fields.Char(
        string="سنة التسلسل",
        compute='_compute_sequence_year',
        store=True,
        index=True
    )

    ticket_month = fields.Char(string="شهر التذكرة", compute="_compute_ticket_month", store=True)
    ticket_week = fields.Char(string="أسبوع التذكرة", compute="_compute_ticket_week", store=True)

    ticket_count = fields.Integer(string="عدد التذاكر", default=1, help="يُستخدم للعد في عرض Pivot")


    is_today = fields.Boolean(compute="_compute_date_flags", store=True)
    is_this_week = fields.Boolean(compute="_compute_date_flags", store=True)
    is_this_month = fields.Boolean(compute="_compute_date_flags", store=True)


    request_archive_by = fields.Many2one('res.users', string="طلب الأرشفة بواسطة", readonly=True)
    request_archive_date = fields.Datetime(string="تاريخ طلب الأرشفة", readonly=True)


    @api.depends('ticket_date')
    def _compute_date_flags(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_today = rec.ticket_date.date() == today if rec.ticket_date else False
            rec.is_this_week = rec.ticket_date.isocalendar()[1] == today.isocalendar()[1] if rec.ticket_date else False
            rec.is_this_month = rec.ticket_date.month == today.month and rec.ticket_date.year == today.year if rec.ticket_date else False


    def action_mark_waiting_archive(self):
        for ticket in self:
            ticket.wait_archive = True
            ticket.request_archive_by = self.env.user
            ticket.request_archive_date = fields.Datetime.now()

            # سجل في المحادثات
            ticket.message_post(
                body=_("📦 تم طلب أرشفة المذكرة من قبل: <b>%s</b> في <i>%s</i>") % (
                    ticket.request_archive_by.name,
                    ticket.request_archive_date.strftime('%Y-%m-%d %H:%M')
                )
            )

            # إرسال تنبيه إلى مدير القسم
            if ticket.department_id and ticket.department_id.manager_id and ticket.department_id.manager_id.user_id:
                manager_user = ticket.department_id.manager_id.user_id
                ticket.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=manager_user.id,
                    summary='طلب أرشفة جديد',
                    note=_("المستخدم <b>%s</b> طلب أرشفة المذكرة رقم <b>%s</b> في التاريخ <i>%s</i>.") % (
                        ticket.request_archive_by.name,
                        ticket.number,
                        ticket.request_archive_date.strftime('%Y-%m-%d %H:%M')
                    )
                )


    @api.depends('ticket_date')
    def _compute_ticket_month(self):
        for record in self:
            if record.ticket_date:
                record.ticket_month = record.ticket_date.strftime('%m')
            else:
                record.ticket_month = False

    @api.depends('ticket_date')
    def _compute_ticket_week(self):
        for record in self:
            if record.ticket_date:
                record.ticket_week = record.ticket_date.strftime('%U')  # الأسبوع في السنة
            else:
                record.ticket_week = False


    @api.depends('ticket_date')
    def _compute_ticket_date_date(self):
        for record in self:
            record.ticket_date_date = record.ticket_date.date() if record.ticket_date else False

    @api.depends('ticket_date')
    def _compute_sequence_year(self):
        for record in self:
            if record.ticket_date:
                record.sequence_year = record.ticket_date.strftime('%Y')
            else:
                record.sequence_year = fields.Date.today().strftime('%Y')

    @api.depends('ticket_date')
    def _compute_sequence_year(self):
        for record in self:
            if record.ticket_date:
                record.sequence_year = record.ticket_date.strftime('%Y')
            else:
                record.sequence_year = fields.Date.today().strftime('%Y')

    @api.model
    def _get_next_number(self):
        """Generate next number based on ticket type, section and creation date"""
        today = fields.Date.today()
        year = today.strftime('%Y')
        
        if not self.ticket_type or not self.ticket_section_id:
            return _('New')
            
        # بناء اسم التسلسل الديناميكي
        sequence_code = f"docflex.ticket.{self.ticket_type.code}.{self.ticket_section_id.code or 'default'}.{year}"
        
        # البحث عن التسلسل أو إنشائه إذا لم يوجد
        sequence = self.env['ir.sequence'].search([
            ('code', '=', sequence_code),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not sequence:
            sequence = self.env['ir.sequence'].create({
                'name': f'Ticket Sequence - {self.ticket_type.name} - {self.ticket_section_id.name} - {year}',
                'code': sequence_code,
                'prefix': f"{self.ticket_type.code}/{self.ticket_section_id.code or 'GEN'}/%(year)s/",
                'padding': 4,
                'number_next': 1,
                'number_increment': 1,
                'company_id': self.company_id.id,
            })
        
        return sequence.next_by_id()

    @api.model
    def _get_default_ticket_type(self):
        """Get the first available ticket_type with context support"""
        code = self._context.get('code')
        domain = [('code', '=', code)] if code else []
        ticket_type = self.env['ticket.type'].search(domain, order='id asc', limit=1)
        return ticket_type.id if ticket_type else False

    @api.depends('department_id')
    def _compute_domain_user_ids(self):
        for record in self:
            user_ids = []
            if record.department_id:
                # ابحث عن كل الموظفين في القسم المحدد
                employees = self.env['hr.employee'].search([('department_id', '=', record.department_id.id)])
                # اجمع المستخدمين المرتبطين بالموظفين
                user_ids = employees.mapped('user_id.id')
            record.domain_user_ids = [Command.set(user_ids)]

    def _get_partner_email_update(self):
        # منطق التحقق من التحديث
        self.ensure_one()
        return self.partner_email != self.partner_from_id.email if self.partner_from_id else False
    
    @api.depends('partner_email', 'partner_from_id')
    def _compute_is_partner_email_update(self):
        for ticket in self:
            ticket.is_partner_email_update = ticket._get_partner_email_update()
    @api.depends('partner_from_id')
    def _compute_partner_name(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_name = ticket.partner_from_id.name

    @api.depends('partner_from_id.phone')
    def _compute_partner_phone(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_phone = ticket.partner_from_id.phone
            
    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_from_id.phone and self.partner_phone != self.partner_from_id.phone:
            ticket_phone_formatted = self.partner_phone or False
            partner_phone_formatted = self.partner_from_id.phone or False
            return ticket_phone_formatted != partner_phone_formatted
        return False
    @api.depends('partner_from_id.email')
    def _compute_partner_email(self):
        for ticket in self:
            if ticket.partner_from_id:
                ticket.partner_email = ticket.partner_from_id.email
    def _inverse_partner_email(self):
        for ticket in self:
            if ticket._get_partner_email_update():
                ticket.partner_from_id.email = ticket.partner_email
    def _inverse_partner_phone(self):
        for ticket in self:
            if ticket._get_partner_phone_update() or not ticket.partner_from_id.phone:
                ticket.partner_from_id.phone = ticket.partner_phone

    @api.depends('partner_phone', 'partner_from_id')
    def _compute_is_partner_phone_update(self):
        for ticket in self:
            ticket.is_partner_phone_update = ticket._get_partner_phone_update()

    
    # def action_archive_ticket(self):
    #     for ticket in self:
    #         ticket.active = False
    #         ticket.archive = True  # استخدام منطقي للحقل المخصص
    #         ticket.wait_archive = False
    #         ticket.message_post(body="✅ تم أرشفة المذكرة.")

    # def action_restore_ticket(self):
    #     for ticket in self:
    #         ticket.active = True
    #         ticket.archive = False
    #         ticket.message_post(body="✅ تم استرجاع المذكرة من الأرشيف.")

    @api.model
    def _get_default_stage(self):
        stage = self.env['docflex.ticket.stage'].search([], order='sequence asc', limit=1)
        if not stage:
            template = self.env.ref('docflex.email_template_docflex_ticket_default', raise_if_not_found=False)
            stage = self.env['docflex.ticket.stage'].create({
                'name': 'جديد',
                'sequence': 1,
                'is_starting': True,
                'template_id': template.id if template else False,
            })
        return stage.id

    
    @api.model
    def create(self, vals):
        # 1. تعيين معلومات المستخدم
        user = self.env.user
        vals.update({
            'user_id': user.id,
            'user_name': user.name,
        })
        
        # 2. تعيين القسم من الموظف
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        if employee and employee.department_id:
            vals['department_id'] = employee.department_id.id
        
        # 3. تعيين المرحلة الافتراضية إذا لم يتم تحديدها
        if 'stage_id' not in vals or not vals.get('stage_id'):
            vals['stage_id'] = self._get_default_stage()
        
        # 4. توليد الرقم التسلسلي
        if vals.get('number', _('New')) == _('New'):
            temp_vals = vals.copy()
            if 'company_id' not in temp_vals:
                temp_vals['company_id'] = self.env.company.id
            temp_ticket = self.new(temp_vals)
            vals['number'] = temp_ticket._get_next_number()
        
        # 5. التأكد من وجود القيم المطلوبة
        required_fields = ['ticket_type', 'ticket_section_id']
        for field in required_fields:
            if field not in vals:
                raise ValidationError(_("حقل %s مطلوب لإنشاء المذكرة") % field)
        
        # 6. إنشاء المذكرة
        ticket = super(DoflexTicket, self).create(vals)
        
        # 7. تسجيل في السجل
        ticket.message_post(body=_("تم إنشاء المذكرة برقم %s") % ticket.number)

            # إرسال البريد الإلكتروني إذا كان هناك قالب مرتبط بالمرحلة
        if ticket.stage_id.template_id:
            ticket.stage_id.template_id.send_mail(ticket.id, force_send=True)
        
        return ticket

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for ticket in self:
            if ticket.kanban_state == 'normal':
                ticket.kanban_state_label = ticket.legend_normal
            elif ticket.kanban_state == 'blocked':
                ticket.kanban_state_label = ticket.legend_blocked
            else:
                ticket.kanban_state_label = ticket.legend_done

    

    def action_open_docflex_ticket(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("docflex.docflex_ticket_action_main_tree")
        action.update({
            'domain': [('stage_id', 'in', self.ids)],
            'context': {
                'default_stage_id': self.id,
            },
        })
        return action

    # إضافة فهارس لتحسين أداء البحث
    
    def _auto_init(self):
        res = super(DoflexTicket, self)._auto_init()
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_number_idx 
            ON docflex_ticket (number)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_date_idx 
            ON docflex_ticket (ticket_date)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_type_idx 
            ON docflex_ticket (ticket_type)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_section_idx 
            ON docflex_ticket (ticket_section_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_status_idx 
            ON docflex_ticket (ticket_status_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_priority_idx 
            ON docflex_ticket (ticket_priority_id)
        """)
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS docflex_ticket_security_idx 
            ON docflex_ticket (ticket_security_id)
        """)
        return res



    is_urgent = fields.Boolean(compute='_compute_is_urgent', store=True)

    @api.depends('ticket_priority_id')
    def _compute_is_urgent(self):
        for rec in self:
            rec.is_urgent = rec.ticket_priority_id.name == 'عاجل'