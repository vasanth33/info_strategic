
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.onchange('user_id')
    def _onchange_user(self):  # pragma: no cover
        """Don't change date_start when changing the user_id. This screws up
        the default value passed by context when creating a record. It's also
        a nonsense to chain both values.
        """
        old_date_start = self.date_start
        super(ProjectTask, self)._onchange_user()
        if old_date_start > self.date_start:
            self.date_start = old_date_start

    task_stage_color = fields.Selection([('red', 'Red'), ('blue', 'Blue'), ('green', 'Green')],
                                        related='stage_id.stage_color',
                                        store=True)

class Project(models.Model):
    _inherit = "project.project"


    task_stage_color = fields.Selection([('red', 'Red'), ('blue', 'Blue'), ('green', 'Green')],)
    
    
class AddStageColor(models.Model):
    _inherit = 'project.task.type'

    stage_color = fields.Selection([('red', 'Red'), ('blue', 'Blue'), ('green', 'Green')],
                                   string='Color in Timeline', default='blue')


    #new_color = fields.Char('New Color', widget='color')



