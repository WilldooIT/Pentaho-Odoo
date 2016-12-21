# -*- coding: utf-8 -*-

{
    'name': 'Report Scheduler',
    "version": "2.0",
    'summary':'Report Scheduler',
    'description': """
Report Email / Message Scheduler
================================

This module provides a simple scheduler running daily reports. The reports may not accept any parameters.

The module "Report Scheduler Selection Sets" (pentaho_report_scheduler_selection_sets) module extends this module
and allows Pentaho reports to be scheduled with pre-entered selections.

Chosen reports can be either emailed to users or sent to their Odoo message box as a notification, or both.

A new option is added to the menus:
    * **Settings / Technical / Automation / Report Scheduler**

From here, a report schedule group can be defined.  The description will be included in the message or email body.

Once defined, the schedule group needs to be associated with a standard Odoo schedule task.  (An example
schedule task is created by this module, and is titled **Report Email Scheduler**). On the **Technical Data** tab,
the name of the schedule group needs to be included in the action argument.

e.g. *('Report Group 1',)*

Note the **comma** after the argument **IS** required.
""",
    "category": "Reporting subsystems",
    "author": "Richard deMeester, WilldooIT",
    'website': 'https://www.willdooit.com',
    'images': [],
    'depends': ['base',
                ],
    'data': ['scheduler.xml',
             'scheduler_view.xml',
             'security/ir.model.access.csv',
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,

    'test': [],
    'css': [],
    'js': [],
}
