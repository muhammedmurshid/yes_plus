from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError


class YesPlusAttendanceForFiveDays(models.Model):
    _name = 'yes_plus.attendance'

    student_name = fields.Char('Student Name')
    day_one = fields.Selection([('present', 'Present'), ('absent', 'Absent')], 'Day 1')
    day_two = fields.Selection([('present', 'Present'), ('absent', 'Absent')], 'Day 2')
    day_three = fields.Selection([('present', 'Present'), ('absent', 'Absent')], 'Day 3')
    day_four = fields.Selection([('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')], 'Day 4')
    day_five = fields.Selection([('full_day', 'Full Day'), ('half_day', 'Half Day'), ('absent', 'Absent')], 'Day 5')
    yes_plus_attendance_id = fields.Many2one('yes_plus.logic')
    date = fields.Date('Date')
    student_id = fields.Integer()
    day_one_check = fields.Boolean()
    day_two_check = fields.Boolean()
    day_three_check = fields.Boolean()
    day_four_check = fields.Boolean()
    day_five_check = fields.Boolean()
