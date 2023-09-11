from odoo import models, api, fields, _
from odoo.exceptions import UserError
import serial
from openerp.tools.translate import _
from datetime import date, datetime, timedelta


class YesPlus(models.Model):
    _name = 'yes_plus.logic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Yes Plus'

    name = fields.Char(string='Name')
    date_one = fields.Date('Day One')
    date_two = fields.Date('Day Two')
    date_three = fields.Date('Day Three')
    date_four = fields.Date('Day Four')
    date_five = fields.Date('Day Five')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('complete', 'Completed'), ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
    )
    batch_id = fields.Many2one('logic.base.batch', string='Batch', required=True)
    yes_attendance_ids = fields.One2many('yes_plus.attendance', 'yes_plus_attendance_id', string='Attendance')

    def action_submit(self):
        batch = self.env['logic.base.batch'].search([])
        for i in batch:
            if self.batch_id.id == i.id:
                self.state = 'confirm'
                if self.date_one:
                    if not i.from_date <= self.date_one <= i.to_date:
                        raise UserError('Day one Date from must be less than date to')
                elif self.date_two:
                    if not i.from_date <= self.date_two <= i.to_date:
                        raise UserError('Day two Date to must be less than date to')
                elif self.date_three:
                    if not i.from_date <= self.date_three <= i.to_date:
                        raise UserError('Day three Date to must be less than date to')
                elif self.date_four:
                    if not i.from_date <= self.date_four <= i.to_date:
                        raise UserError('Day four Date to must be less than date to')

                elif self.date_five:
                    if not i.from_date <= self.date_five <= i.to_date:
                        raise UserError('Day five Date to must be less than date to')

                else:
                    self.state = 'confirm'

    @api.onchange('batch_id')
    def onchange_batch_id(self):
        students = self.env['logic.students'].search([('batch_id', '=', self.batch_id.id)])
        unlink_commands = [(3, child.id) for child in self.yes_attendance_ids]
        self.write({'yes_attendance_ids': unlink_commands})
        abc = []
        for i in students:
            res_list = {
                'student_name': i.name,
                'student_id': i.id,

            }
            abc.append((0, 0, res_list))
        self.yes_attendance_ids = abc

    def action_confirm(self):
        # student = self.env['logic.students'].search(
        #     [('id', 'in', [stud.student_id for stud in self.yes_attendance_ids])])
        # print(student, 'rrr')
        # print([stud.student_id for stud in self.yes_attendance_ids])
        # students = []
        # for rec in student:
        #     for i in self.yes_attendance_ids:
        #         print(i.id, 'id')
        #         # print(str(k.student_id), 'student id')
        #         if rec.id == i.student_id:
        #             print('yeaa')
        #
        #             stdt = {
        #                 'name': i.student_name,
        #                 'attendance': i.attendance,
        #                 'date': self.date_one,
        #                 'stud_id': i.student_id
        #             }
        #             students.append((0, 0, stdt))
        #             rec.yes_plus_att_ids = students
        #
        #         else:
        #             print('noo')
        #         std = self.env['logic.students'].search([])
        #         for jk in std:
        #             for jkm in jk.yes_plus_att_ids:
        #                 print(jkm.name, 'name')
        #                 if jkm.stud_id != jk.id:
        #                     jkm.unlink()

        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('yes_plus.mail_yes_plus_coordinator_alert').id)])
        activity_id.action_feedback(feedback=f'Yes Plus Done')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('yes_plus.mail_yes_plus_coordinator_alert').id)])
        other_activity_ids.unlink()
        # activity_id.unlink()
        self.state = 'complete'

    def action_cancel(self):
        self.state = 'cancel'

    def coordinator_alert_message(self):
        activities_to_remind = self.env['yes_plus.logic'].search([])
        print(activities_to_remind, 'activities_to_remind')
        # if jj.state not in 'confirm':
        #     jj.state_bool = True
        for i in activities_to_remind:
            one_day_before = i.date_one - timedelta(days=1)
            print(one_day_before, 'before')
            if one_day_before == datetime.now().date():
                print(i.name, 'rec')
                if i.state == 'confirm':
                    users = activities_to_remind.env.ref('yes_plus.yes_plus_coordinator').users
                    for j in users:
                        i.activity_schedule('yes_plus.mail_yes_plus_coordinator_alert', user_id=j.id,
                                            note=f'Tomorrow: Yes Plus reminder.')
            # if i.state == 'submit':

    def mail_for_hr_activity(self):
        today = fields.Datetime.now()
        ss = self.env['yes_plus.logic'].search([])
        users = ss.env.ref('yes_plus.yes_plus_hr_manager').users
        for j in users:
            for i in ss:
                if i.state == 'confirm':
                    date_1_days_later = i.date_one + timedelta(days=1)
                    print(date_1_days_later, 'del')
                    if date_1_days_later == today.date():
                        i.activity_schedule('yes_plus.mail_yes_plus_coordinator_alert', user_id=j.id,
                                            note=f'Delayed: Yes Plus is running behind schedule.')
