# -*- coding: utf-8 -*-

{
    'name': 'Report Scheduler Selection Sets',
    "version": "2.0",
    'summary':'Report Scheduler with Selection Sets',
    'description': """
Report Scheduler with Selection Sets
====================================

This module provides extends the report scheduler and allows the scheduling of Pentaho reports that have
pre-defined selection sets.

The desired selection set to be used needs to be chosen in the report schedule group.
""",
    "category": "Reporting subsystems",
    "author": "Richard deMeester, WilldooIT",
    'website': 'https://www.willdooit.com',
    'images': [],
    'depends': ['pentaho_report_selection_sets',
                'pentaho_report_scheduler',
                ],
    'data': ['scheduler_view.xml',
            ],
    'demo': [],
    'qweb': [],
    'installable': False, # Until further notice
    'application': False,
    'auto_install': True,

    'test': [],
    'css': [],
    'js': [],
}
