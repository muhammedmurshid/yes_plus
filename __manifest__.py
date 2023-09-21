{
    'name': "Yes Plus",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/yes_plus_rules.xml',
        'views/yes_plus.xml',
        'data/cron_job.xml',

    ],
    'demo': [],
    'summary': "yes_plus_logic",
    'description': "this_is_yes_plus_module",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
