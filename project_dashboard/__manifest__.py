# -*- coding: utf-8 -*-

{
    'name': "Info Strategic Project Management",
    'description': """Customized module for Project management by Info Strategic""",
     'summary': 'Customized module for Project management',
    'author': 'Info Strategic',
    'website': "http://www.infostrategic.com/",
    'category': 'Project',
    'version': '11.0',
    'depends': ['base', 'project','account','hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project_plan_view.xml',
        'views/header.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [],
    'installable': True,
    'auto_install': False,
}
