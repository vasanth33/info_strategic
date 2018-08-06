# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class StrategicPlan(models.Model):
    _name = "strategic.plan"

    name = fields.Char()
    description = fields.Html(copy=False)
    start_date = fields.Date(copy=False)
    end_date = fields.Date(copy=False)
    strategic_goal_count = fields.Integer(compute='_compute_strategic_goal_count', string="Number of documents attached",copy=False)

    def _compute_strategic_goal_count(self):
        strategic_goal_ids = self.env['strategic.goal'].search([('strategic_plan_id', '=', self.id)])
        self.strategic_goal_count = len(strategic_goal_ids)
            
    @api.multi
    def strategic_goal_tree_view(self):
        strategic_goal_ids = self.env['strategic.goal'].search([('strategic_plan_id', '=', self.id)])
        view_id = self.env['ir.model.data'].get_object_reference('project_dashboard', 'strategic_goal_tree_view')[1]
        return {
           'type': 'ir.actions.act_window',
           'name': _('Strategic Goals'),
           'res_model': 'strategic.goal',
           'view_type': 'form',
           'view_id': view_id,
           'view_mode': 'tree',
           'target': 'current',
           'nodestroy': True,
           'domain': [('id', 'in', strategic_goal_ids.ids)],
       }


class StrategicGoal(models.Model):
    _name = "strategic.goal"

    name = fields.Char()
    description = fields.Html(copy=False)
    start_date = fields.Date(copy=False)
    end_date = fields.Date(copy=False)
    strategic_plan_id = fields.Many2one('strategic.plan', string="Strategic Plan",copy=False)
    operational_goal_count = fields.Integer(compute='_compute_operational_goal_count', string="Number of documents attached",copy=False)

    def _compute_operational_goal_count(self):
        operational_goal_ids = self.env['operational.goal'].search([('strategic_goal_id', '=', self.id)])
        self.operational_goal_count = len(operational_goal_ids)
            
    @api.multi
    def operational_goal_tree_view(self):
        operational_goal_ids = self.env['operational.goal'].search([('strategic_goal_id', '=', self.id)])
        view_id = self.env['ir.model.data'].get_object_reference('project_dashboard', 'operational_goal_tree_view')[1]
        return {
           'type': 'ir.actions.act_window',
           'name': _('Operational Goals'),
           'res_model': 'operational.goal',
           'view_type': 'form',
           'view_id': view_id,
           'view_mode': 'tree',
           'target': 'current',
           'nodestroy': True,
           'domain': [('id', 'in', operational_goal_ids.ids)],
       }

    
class OperationalGoal(models.Model):
    _name = "operational.goal"

    name = fields.Char()
    description = fields.Html(copy=False)
    start_date = fields.Date(copy=False)
    end_date = fields.Date(copy=False)
    strategic_goal_id = fields.Many2one('strategic.goal', string="Strategic Goal",copy=False)

    
class Project(models.Model):
    _inherit = "project.project"
    
    strategic_plan_id = fields.Many2one('strategic.plan', string="Strategic Plan")
    strategic_goal_id = fields.Many2one('strategic.goal', string="Strategic Goal")
    operational_goal_id = fields.Many2one('operational.goal', string="Operational Goal")
    department_id = fields.Many2one('hr.department', string="Department")
    year = fields.Selection([(num, str(num)) for num in range(2000, (datetime.now().year) + 1)], 'Year')
    country_id = fields.Many2one('res.country', String="Benefited Country")
    in_budget = fields.Integer(string='Foundation Budget',copy=False)
    out_budget = fields.Integer(string='Donor Budget',copy=False)
    start_date = fields.Date()
    end_date = fields.Date()
    beneficiaries = fields.Integer()
    description = fields.Html(string= 'Project Description',copy=False)
    completion_rate = fields.Float(compute="_get_project_completion", string="Completion rate (%)")
    project_completion = fields.Float(compute="_get_project_completion", string="Project Completion (%)")
    image_ids = fields.One2many('project.image', 'project_id', string='Images')
    total_budget = fields.Float(compute="_get_total_budget", string="Total Budget")
    agency_id = fields.Many2one('res.partner',string='Agency')
    donor_id = fields.Many2one('res.partner',string='Donor')
    agent_id = fields.Many2one('res.partner',related='agency_id',store=True, readonly=True)

    contract_ids =  fields.One2many('agent.contract', 'project_id', string='Phases')
    project_type_id = fields.Many2one('project.type',string='Project Type')
    operating_purpose_id =fields.Many2one('operating.purpose',string='Operating Purpose')
    nature_assistance_id = fields.Many2one('nature.assistance',string='Nature Assistance')
    foundation_category_id = fields.Many2one('foundation.category',string='Foundation Category')
    assistance_classification_id = fields.Many2one('assistance.classification',string='Assistance Classification')
    main_sector_id = fields.Many2one('main.sector',string='Main Sector')
    sub_sector_id = fields.Many2one('sub.sector',string='Sub Sector')
    project_goal_id = fields.Many2one('project.goal',string='Goal')
    project_target_id = fields.Many2one('project.target',string='Target')
    project_number = fields.Char(copy=False)
    location_description = fields.Html()
    status = fields.Selection([('new', 'New'), ('progress', 'On Progress'),('end', 'Ended')], 'Project Status', default='new')
    legal_attitude = fields.Html(copy=False)
    financial_attitude = fields.Html(copy=False)
    media_plan = fields.Html(copy=False)
    project_location = fields.Char(string="Project Location")

    @api.depends('project_completion')
    def _get_project_completion(self):
        for project in self:
            task_ids = self.env['project.task'].search([('project_id', '=', project.id)])
            total = 0.0
            completion = 0.0
            for task in task_ids:
                total += (task.task_weight * task.completion_rate) / 100
                completion += task.completion_rate
            if completion:
                total_completion = completion / len(task_ids)
                project.completion_rate = total_completion
                project.project_completion = total
            
    @api.depends('in_budget','out_budget')
    def _get_total_budget(self):
        if self.in_budget or self.out_budget:
            self.total_budget = self.in_budget + self.out_budget
        
    @api.onchange('assistance_classification_id')
    def onchange_assistance_classification_id(self):
        if self.assistance_classification_id:
            main_sector = self.env['main.sector'].search([('assistance_id', '=', self.assistance_classification_id.id)])
            return {'domain': {'main_sector_id': [('id', 'in', main_sector.ids)]}}
     
    @api.onchange('main_sector_id')
    def onchange_main_sector_id(self):
        if self.main_sector_id:
            sub_sectors = self.env['sub.sector'].search([('main_sector_id', '=', self.main_sector_id.id)])
            return {'domain': {'sub_sector_id': [('id', 'in', sub_sectors.ids)]}}
 
    @api.onchange('project_goal_id')
    def onchange_project_goal_id(self):
        if self.project_goal_id:
            targets = self.env['project.target'].search([('goal_id', '=', self.project_goal_id.id)])
            return {'domain': {'project_target_id': [('id', 'in', targets.ids)]}}
        
    @api.onchange('strategic_goal_id')
    def onchange_strategic_goal_id(self):
        if self.strategic_goal_id:
            operational_goal_ids = self.env['operational.goal'].search([('strategic_goal_id', '=', self.strategic_goal_id.id)])
            return {'domain': {'operational_goal_id': [('id', 'in', operational_goal_ids.ids)]}}

    @api.onchange('strategic_plan_id')
    def onchange_strategic_plan_id(self):
        if self.strategic_plan_id:
            strategic_goal_ids = self.env['strategic.goal'].search([('strategic_plan_id', '=', self.strategic_plan_id.id)])
            return {'domain': {'strategic_goal_id': [('id', 'in', strategic_goal_ids.ids)]}}
        
class Task(models.Model):
    _inherit = "project.task"
    
    @api.model
    def _default_payment_method(self):
        return self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','inbound')])
    
    date_start = fields.Date(copy=False)
    date_end = fields.Date(copy=False)
    completion_rate = fields.Integer(string="Completion rate (%)",copy=False) 
    task_weight = fields.Integer(string="task Weight (%)",copy=False)
    initial_cost = fields.Float(string='Initial Cost',copy=False)
    payment_line_ids = fields.One2many('task.payment', 'task_id',copy=False)
    total_payment = fields.Float(compute="_get_payments", string="Payments",copy=False)
    remaining_payments = fields.Float(compute="_get_payments", string="Remaining",copy=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', domain=[('type', 'in', ('bank', 'cash'))],copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id,copy=False)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type',default=_default_payment_method, copy=False)
    disable_post_button = fields.Boolean(default=False,copy=False)
    image_ids = fields.One2many('task.image', 'task_id', string='Images')
    agency_id = fields.Many2one('res.partner',string='Agency',translate=True)
    project_id = fields.Many2one('project.project',
        string='Project',
        default=lambda self: self.env.context.get('default_project_id'),
        index=True,
        track_visibility='onchange',
        change_default=True)
    add_to_project = fields.Boolean(copy=False)
    contract_no = fields.Char(string='Contract No',copy=False)
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Payment Requested'),
                              ('confirmed', 'Payment Confirmed'),
                              ('approved', 'Payment Approved'), ('partial', 'Partial Payment'),('paid', 'Paid'), ('rejected', 'Rejected'),
                              ('cancel', 'Cancel')], 'State', default='draft')
    
    
    @api.model
    def default_get(self,default_fields):
        res = super(Task, self).default_get(default_fields)
        project_id = res.get('project_id',False)
        if project_id:
            project_id = self.env['project.project'].search([('id','=',project_id)])
            res['agency_id'] = project_id.agency_id.id
            res['initial_cost'] = project_id.in_budget + project_id.out_budget
        return res

    @api.multi
    def payment_confirmed(self):
        part_ids = []
        user = self.env['res.users'].browse(self._uid)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
                         subject='Payment Confirmed',
                         body=_(str(user.name) + ' is confirmed the Payment request'),
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'confirmed'

    @api.multi
    def payment_approved(self):
        part_ids = []
        thread_pool = self.env['mail.thread']
        user = self.env['res.users'].browse(self._uid)
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool.message_post(
                         subject='Payment Approved',
                         body=_(str(user.name) + ' is approved the payment request of task')  + self.name,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'approved'

    @api.multi
    def reject_request(self):
        part_ids = []
        thread_pool = self.env['mail.thread']
        user = self.env['res.users'].browse(self._uid)
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool.message_post(
                         subject='Request to Approve',
                         body=_(str(user.name) + ' is rejected the payment request of Task : ') + self.name ,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'rejected'

    @api.multi
    def cancel_request(self):
        part_ids = []
        user = self.env['res.users'].browse(self._uid)
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
                         subject='Request to Approve',
                         body=_(str(user.name) + ' is cancelled the payment request of Task : ') + self.name,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'cancel'

    @api.multi
    def reset(self):
        part_ids = []
        user = self.env['res.users'].browse(self._uid)
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
                         subject='Request to Approve',
                         body=_(str(user.name) + ' is reset the payment request of task : ') + self.name,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )  
        self.state = 'draft'

    @api.multi
    def request_payment(self):
        part_ids = []
        user = self.env['res.users'].browse(self._uid)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        part_ids.append(self.user_id.partner_id.id)
        if self.agency_id:
            part_ids.append(self.agency_id.id)
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
                         subject='Payment Requested',
                         body=_(str(user.name) + ' is requesting to approve his/her payment of Task : ') + self.name,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'requested'
        
    @api.multi
    def post(self):
        if not self.payment_line_ids:
            raise UserError(_('Payment details are empty !!!. Please enter the payment amount.'))
        self.disable_post_button = False
        payment_obj = self.env['account.payment']
        part_ids = []
        for line in self.payment_line_ids:
            vals ={
                'journal_id': self.journal_id.id,
                'payment_method_id': self.payment_method_id.id,
                'payment_date': line.date,
                'communication': self.description or '',
                'payment_type': 'inbound',
                'amount': line.amount,
                'currency_id': self.currency_id.id,
                'partner_id': line.partner_id.id,
                'partner_type': 'customer',
            }
            res = payment_obj.create(vals)
            res.post()
            if self.remaining_payments:
                self.state = 'partial'
            else:
                self.disable_post_button = True
        user = self.env['res.users'].browse(self._uid)
        admin_users = self.env['res.groups'].search([('name', '=', 'Settings')]).mapped('users')
        part_ids.append(self.user_id.partner_id.id)
        part_ids.append(self.agency_id.id)
        for i in admin_users:
            if i.id not in part_ids:
                part_ids.append(i.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
                         subject='Payment Done',
                         body=_(str(user.name) + ' is registered the payment of Task : ') + self.name,
                         needaction_partner_ids=[(6, 0, part_ids)],
                         type='notification',
                         subtype='mail.mt_comment',
                         )
        self.state = 'paid'
        return True
        
    @api.depends('payment_line_ids')
    def _get_payments(self):
        for pay in self:
            total = 0.0
            for record in pay.payment_line_ids:
                total += record.amount
            else:
                pay.total_payment = total
                pay.remaining_payments = pay.initial_cost - total
        
    @api.onchange('task_weight')
    def _onchange_task_weight(self):
        if self.task_weight:
            task_ids = self.search([('project_id', '=', self.project_id.id), ('id', '!=', self._origin.id)])
            weight = 0
            remaining = 0
            for i in task_ids:
                weight += i.task_weight
            remaining = 100 - weight
            if self.task_weight > remaining:
                raise UserError(_('Total task weight cannot be greater than maximum.You can give maximum %s as Task Weight.') % (remaining,))

    @api.model
    def create(self, vals):
        context = dict(self.env.context, mail_create_nolog=True)
        task = super(Task, self.with_context(context)).create(vals)
        if task.initial_cost > task.project_id.total_budget:
            raise UserError(_('Initial cost is greater ten Total Budget.You can give maximum %s as Initial Cost.') % (task.project_id.total_budget,))
        image_ids = vals.get('image_ids',False)
        if image_ids:
            for i in vals['image_ids']:
                if i[2]['add_to_project']:
                    vals ={
                        'image':i[2]['image'],
                        'project_id':task.project_id.id,
                        'task_id':task.id
                    }
                    task.project_id.image_ids.create(vals)
        if task.agency_id:
            vals = {
                'project_id': task.project_id.id,
                'start_date': task.date_start,
                'end_date': task.date_end,
                'contract_no' : task.contract_no,
                'task_id': task.id
                }
            self.env['agent.contract'].create(vals)
            
        return task

    @api.multi
    def write(self, vals):
        if 'image_ids' in vals:
            self.project_id.image_ids.unlink()
            task_ids = self.search([('project_id','=',self.project_id.id)])
            for task in task_ids:
                for i in task.image_ids:
                    if i.add_to_project:
                        vals ={
                            'image':i.image,
                            'project_id':self.project_id.id,
                            'task_id':self.id
                               }
                        self.project_id.image_ids.create(vals)
        contract = self.env['agent.contract'].search([('task_id','=',self.id)])
        if 'contract_no' in vals:
            contract.contract_no = vals['contract_no']
        if 'project_id' in vals:
            contract.project_id = vals['project_id']
        return super(Task, self).write(vals)
    
    @api.multi
    def unlink(self):
        for record in self:
            task_ids = self.env['project.image'].search([('task_id','=',record.id)])
            for task in task_ids:
                task.unlink()
        return super(Task, self).unlink()
    
    
class Taskpayment(models.Model):
    _name = "task.payment"

    name = fields.Char('Description', required=True)
    partner_id = fields.Many2one('res.partner', string='Agency')
    date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
    amount = fields.Float()
    task_id = fields.Many2one('project.task', string='Task')
    
class Taskimage(models.Model):
    _name = 'task.image'

    image = fields.Binary('Image')
    task_id = fields.Many2one('project.task',string='Task')
    project_id = fields.Many2one('project.project',string='Project')
    add_to_project = fields.Boolean(copy=False)
    url = fields.Char(string="URL", required=True)

class ProjectImage(models.Model):
    _name = 'project.image'

    image = fields.Binary('Image')
    task_id = fields.Many2one('project.task',string='Task')
    project_id = fields.Many2one('project.project',string='Project')
    
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
  
    is_agency = fields.Boolean(copy=False)
    is_donor = fields.Boolean(copy=False)
    
class AgentContract(models.Model):
    _name = "agent.contract"
      
    task_id = fields.Many2one('project.task', string='Task')
    start_date = fields.Date(related='task_id.date_start', string='Start Date', copy=False)
    end_date = fields.Date(related='task_id.date_end', string='End Date', copy=False)
    contract_no = fields.Char(string='Contract No',copy=False)
#     sequence_ref = fields.Integer('No.', compute="_sequence_ref")
    project_id = fields.Many2one('project.project', string='Project')
    
    
#     @api.depends('task_id.contract_ids')
#     def _sequence_ref(self):
#         for line in self:
#             no = 1
#             for l in line.order_id.order_line:
#                 no += 1
#                 l.sequence_ref = no
    

class ProjectType(models.Model):
    _name = 'project.type'    

    name = fields.Char(copy=False)
    
class OperatingPurpose(models.Model):
    _name = 'operating.purpose'    

    name = fields.Char(copy=False)
    
class NatureAssistance(models.Model):
    _name = 'nature.assistance'    

    name = fields.Char(copy=False)
    
class FoundationCategory(models.Model):
    _name = 'foundation.category'    

    name = fields.Char(copy=False)
    
class AssistanceClassification(models.Model):
    _name = 'assistance.classification'    

    name = fields.Char(copy=False)
    
class MainSector(models.Model):
    _name = 'main.sector'    

    name = fields.Char(copy=False)
    assistance_id = fields.Many2one('assistance.classification','Assistance',copy=False)
    
class SubSector(models.Model):
    _name = 'sub.sector'    

    name = fields.Char(copy=False)
    main_sector_id = fields.Many2one('main.sector','Main Sector',copy=False)
    
class ProjectGoal(models.Model):
    _name = 'project.goal'    

    name = fields.Char(copy=False)
    
class ProjectTarget(models.Model):
    _name = 'project.target'    

    name = fields.Char(copy=False)
    goal_id = fields.Many2one('project.goal','Goal',copy=False)
