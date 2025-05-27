from odoo import models ,fields, _,api
from random import randint


class TicketPriority(models.Model):
  
    _name = 'ticket.priority'
    _description = _('اولاليات المذكرات')
    def _get_default_color(self):
        return randint(1, 11)
    name=fields.Char(_("الاسم"))
    code = fields.Selection([
        ('highest',_("عاجله ومهمة")),
        ('high',_("عاجلة وغير مهمة")),
        ('Medium',_("غير عاجلة ومهمة")),
        ('low',_("عادية")),
        ('lowset',_("ليست عاجلة وغير مهمة")),
        ('blocker',_("موقفة")),
        ('minor',_("اقلية مجزئة")),
        ('ohter',_("اخرى")),
    ], default='low', string=_("طبيعة الاولولية"))
    active = fields.Boolean(_("نشط"), defualt=True)
    is_default =  fields.Boolean(_("الافتراضية"), defualt=True)
    icon = fields.Binary(_('الايقونة'), attachment=True)

    color = fields.Integer(_('اللون'),default=_get_default_color)

    
    