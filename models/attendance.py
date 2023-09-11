from odoo import models, fields, api, _
from lxml import etree


class YesPlusAttendanceForFiveDays(models.Model):
    _name = 'yes_plus.attendance'

    student_name = fields.Char('Student Name')
    day_one = fields.Boolean('Day 1', default=True,)
    day_two = fields.Boolean('Day 2', default=True)
    day_three = fields.Boolean('Day 3', default=True)
    day_four = fields.Boolean('Day 4', default=True)
    day_five = fields.Boolean('Day 5', default=True)
    yes_plus_attendance_id = fields.Many2one('yes_plus.logic')
    date = fields.Date('Date')
    student_id = fields.Integer()

    # @api.onchange('date')
    # def _onchange_fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     print('kkk')
    #     if view_type == 'form':
    #         doc = etree.XML(result['arch'])
    #         sale_reference = doc.xpath("//field[@name='date']")
    #         if sale_reference:
    #             sale_reference[0].set("string", "Sale Order")
    #             sale_reference[0].addnext(etree.Element('label', {'string': 'Sale Reference Number'}))
    #             result['arch'] = etree.tostring(doc, encoding='unicode')
    #
    #     return result
