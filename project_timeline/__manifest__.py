
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project timeline",
    "summary": "Timeline view for projects",
    "version": "11.0.1.0.0",
    "category": "Project Management",
    "website": "https://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "project",
        "web_timeline",
    ],
    "data": [
        "views/project_task_view.xml",
        "views/project_view.xml",
    ],
    "demo": [
        'demo/project_task_demo.xml',
    ]
}
