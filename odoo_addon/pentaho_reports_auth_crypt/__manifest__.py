# -*- coding: utf-8 -*-

{
    'name': 'Pentaho For Encrypted Passwords',
    "version": "2.0",
    'summary':'Pentaho For Encrypted Passwords',
    'description': """
Pentaho For Encrypted Passwords
===============================

This module provides support for Pentaho Reports where the auth_crypt (password encryption)
module has been installed.
""",
    "category": "Reporting subsystems",
    "author": "Richard deMeester, WilldooIT",
    'website': 'https://www.willdooit.com',
    'images': [],
    'depends': ['pentaho_reports',
                'auth_crypt',
                ],
    'data': ['security/ir.model.access.csv',
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': True,

    'test': [],
    'css': [],
    'js': [],
}
