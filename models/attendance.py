from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError


class YesPlusAttendanceForFiveDays(models.Model):
    _name = 'yes_plus.attendance'

    student_name = fields.Char('Student Name')
    day_one = fields.Boolean('Day 1', default=True)
    day_two = fields.Boolean('Day 2', default=True)
    day_three = fields.Boolean('Day 3', default=True)
    day_four = fields.Selection([('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')], 'Day 4', default='full_day')
    day_five = fields.Selection([('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')], 'Day 5', default='full_day')
    yes_plus_attendance_id = fields.Many2one('yes_plus.logic')
    date = fields.Date('Date')
    student_id = fields.Integer()
    day_one_check = fields.Boolean()
    day_two_check = fields.Boolean()
    day_three_check = fields.Boolean()
    day_four_check = fields.Boolean()
    day_five_check = fields.Boolean()
