# -*- encoding: utf-8 -*-

{
    "name": "Pentaho Report Selections Saving",
    "version": "2.0",
    'summary':'Pentaho Report Selections Saving and Recalling',
    "description": """
Pentaho - Report Selections Saving
==================================

This module builds on the Odoo Pentaho Report functionality by allowing report selections to be stored and
retrieved.  Those selections can have a dynamic element by using selection default functions.

To be able to store and maintain selection sets, a user must have their security set accordingly.
""",
    "category": "Reporting subsystems",
    "author": "Richard deMeester, WilldooIT",
    'website': 'https://www.willdooit.com',
    'images': [],
    "depends": ["pentaho_reports",
                ],
    "data": ["security/pentaho_selection_set_security.xml",
             "security/ir.model.access.csv",
             "wizard/store_selections.xml",
             "report_prompt.xml",
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
