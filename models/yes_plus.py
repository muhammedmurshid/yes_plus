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
    trainer_name = fields.Char(string='Trainer Name', required=True)
    date = fields.Date('Added Date', required=True, default=lambda self: fields.Date.context_today(self))
    date_one = fields.Date('Day One')
    date_two = fields.Date('Day Two')
    date_three = fields.Date('Day Three')
    date_four = fields.Date('Day Four')
    date_five = fields.Date('Day Five')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('academic_head_approve', 'Academic Head Approval'), ('accounts_approval', 'Accountant Approval'),
         ('complete', 'Completed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
    )
    coordinator_id = fields.Many2one('res.users', string='Assign to Coordinator',
                                     related='batch_id.academic_coordinator')
    batch_id = fields.Many2one('logic.base.batch', string='Batch', required=True)
    branch = fields.Many2one('logic.base.branches', related='batch_id.branch_id', string='Branch')
    course_id = fields.Many2one('logic.base.courses', string='Course', related='batch_id.course_id')
    yes_attendance_ids = fields.One2many('yes_plus.attendance', 'yes_plus_attendance_id', string='Attendance')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    programme_coordinator = fields.Many2one('res.users', string='Programme Coordinator',
                                            default=lambda self: self.env.user, readonly=True)
    digital_support_received = fields.Boolean(string='Digital Support Received')
    rating = fields.Selection(
        selection=[('0', 'No rating'), ('1', 'Very Poor'), ('2', 'Poor'), ('3', 'Average'), ('4', 'Good'),
                   ('5', 'Very Good')], string="Rating", default='0')

    @api.depends('make_visible_academic_head_yes_plus', 'batch_id')
    def _compute_academic_head_yes_plus(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('yes_plus.academic_head_yes_plus'):
            self.make_visible_academic_head_yes_plus = True
        else:
            self.make_visible_academic_head_yes_plus = False

    make_visible_academic_head_yes_plus = fields.Boolean(string="User", compute='_compute_academic_head_yes_plus')

    # def _compute_display_name(self):
    #     for rec in self:
    #         if rec.name:
    #             rec.display_name = rec.name + ' - ' + rec.trainer_name
    #         else:
    #             rec.display_name = rec.trainer_name

    def action_submit(self):
        batch = self.env['logic.base.batch'].search([])
        for i in batch:
            if self.batch_id.id == i.id:
                self.state = 'confirm'
                if self.batch_id.from_date and self.batch_id.to_date:
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
        student = self.env['logic.students'].search(
            [('id', 'in', [stud.student_id for stud in self.yes_attendance_ids])])
        print(student, 'rrr')
        print([stud.student_id for stud in self.yes_attendance_ids])
        students = []
        for rec in student:
            for i in self.yes_attendance_ids:
                if rec.id == i.student_id:
                    if i.day_one == True:
                        rec.day_one_date = self.date_one
                        rec.day_one = 'present'
                    else:
                        rec.day_one_date = self.date_one
                        rec.day_one = 'absent'
                    if i.day_two == True:
                        rec.day_two_date = self.date_two
                        rec.day_two = 'present'
                    else:
                        rec.day_two_date = self.date_two
                        rec.day_two = 'absent'
                    if i.day_three == True:
                        rec.day_three_date = self.date_three
                        rec.day_three = 'present'
                    else:
                        rec.day_three_date = self.date_three
                        rec.day_three = 'absent'

                    rec.day_four = i.day_four
                    rec.day_four_date = self.date_four
                    rec.day_five = i.day_five
                    rec.day_five_date = self.date_five

        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('yes_plus.mail_yes_plus_coordinator_alert').id)])
        activity_id.action_feedback(feedback=f'Yes Plus Done')
        # other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
        #     'activity_type_id', '=', self.env.ref('yes_plus.mail_yes_plus_coordinator_alert').id)])
        # other_activity_ids.unlink()
        # activity_id.unlink()
        self.state = 'academic_head_approve'

    def action_cancel(self):
        self.state = 'cancel'

    def coordinator_alert_message(self):
        activities_to_remind = self.env['yes_plus.logic'].search([])
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

    @api.onchange('date_one', 'date_two', 'date_three', 'date_four', 'date_five')
    def yes_plus_date_one_test(self):
        print('yes')
        for rec in self:
            if rec.date_one:
                rec.yes_attendance_ids.day_one_check = True
            else:
                rec.yes_attendance_ids.day_one_check = False
            if rec.date_two:
                rec.yes_attendance_ids.day_two_check = True
            else:
                rec.yes_attendance_ids.day_two_check = False
            if rec.date_three:
                rec.yes_attendance_ids.day_three_check = True
            else:
                rec.yes_attendance_ids.day_three_check = False
            if rec.date_four:
                rec.yes_attendance_ids.day_four_check = True
            else:
                rec.yes_attendance_ids.day_four_check = False
            if rec.date_five:
                rec.yes_attendance_ids.day_five_check = True
            else:
                rec.yes_attendance_ids.day_five_check = False

    def approval_for_academic_head(self):
        if self.coordinator_id.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'accounts_approval'
        else:
            raise UserError('You are not authorized')

    def accounts_approval(self):
        self.state = 'complete'

    @api.depends('yes_attendance_ids')
    def _compute_attendance(self):
        for rec in self:
            rec.attended_counts = len(rec.yes_attendance_ids)

    attended_counts = fields.Integer(compute='_compute_attendance', store=True)

    @api.depends('batch_id')
    def _compute_total_batch_strength(self):
        for rec in self:
            rec.batch_strength = len(rec.yes_attendance_ids)

    batch_strength = fields.Integer(compute='_compute_total_batch_strength', store=True)

    @api.depends('yes_attendance_ids.day_one', 'yes_attendance_ids.day_two', 'yes_attendance_ids.day_three',
                 'yes_attendance_ids.day_four', 'yes_attendance_ids.day_five')
    def _compute_yes_plus_avg_attendance(self):
        for record in self:
            if record.yes_attendance_ids:
                total_attendance = 0
                for yes in record.yes_attendance_ids:
                    if record.date_one:
                        if yes.day_one == True:
                            total_attendance += 1
                        elif yes.day_one == False:
                            total_attendance += 0
                    if record.date_two:
                        if yes.day_two == True:
                            total_attendance += 1
                        elif yes.day_two == False:
                            total_attendance += 0
                    if record.date_three:
                        if yes.day_three == True:
                            total_attendance += 1
                        elif yes.day_three == False:
                            total_attendance += 0
                    if record.date_four:
                        if yes.day_four == 'full_day':
                            total_attendance += 1
                        elif yes.day_four == 'half_day':
                            total_attendance += 0.5
                    if record.date_five:
                        if yes.day_five == 'full_day':
                            total_attendance += 1
                        elif yes.day_five == 'half_day':
                            total_attendance += 0.5
                if record.date_one and record.date_two and record.date_three and record.date_four and record.date_five:
                    record.yes_avg_attendance = total_attendance / 5
                elif record.date_one and record.date_two and record.date_three and record.date_four:
                    record.yes_avg_attendance = total_attendance / 4
                elif record.date_one and record.date_two and record.date_three:
                    record.yes_avg_attendance = total_attendance / 3
                elif record.date_one and record.date_two:
                    record.yes_avg_attendance = total_attendance / 2
                else:
                    record.yes_avg_attendance = total_attendance
            else:
                record.yes_avg_attendance = 0
        # print(self.yes_avg_attendance, 'yes_avg_attendance')

    yes_avg_attendance = fields.Float(compute='_compute_yes_plus_avg_attendance', store=True,
                                      string='Yes Plus Average Attendance')
