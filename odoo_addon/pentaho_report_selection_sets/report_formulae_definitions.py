# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.addons.pentaho_reports import java_odoo

from odoo.tools.translate import _

FTYPE_TIMEDELTA = 'tdel'
FUNCTION_TYPES = java_odoo.ODOO_DATA_TYPES + [(FTYPE_TIMEDELTA, 'Time Delta')]


# FORMULAE are defined as dictionaries:
#
#    key is the formula name to be recognised in the parameter evaluation
#
#    value is a dictionary:
#        'type' : type of value this formula returns
#        'type_2m' : true if formula returns a list of values
#        'call' : the actual formula call, with place holders defined as %x
#        'arguments' : a list of dictionaries to define acceptable arguments.
#                        'name' : argument name or undefined for positional arguments
#                        'types' : list of valid types this argument can accept
#                        'lists' : arguments can be lists or not
#                        'insert_at' : which place-holder this should be inserted at - if more than one defined for same 'insert_at', they will be comma separated
#                        'insert_as' : value will be inserted as a named argument using this as the name - if not defined, then name will be used - if that is undefined, then value only will be inserted


FORMULAE = {'now': {'type': java_odoo.TYPE_TIME,
                    'call': 'self.localise(datetime.now())',
                    'arguments': [],
                    },
            'today': {'type': java_odoo.TYPE_DATE,
                      'call': 'self.localise(datetime.now()).date()',
                      'arguments': [],
                      },
            'start_of_month': {'type': java_odoo.TYPE_DATE,
                               'call': 'self.localise(datetime.now()).date() + relativedelta(day=1)',
                               'arguments': [],
                               },
            'start_of_year': {'type': java_odoo.TYPE_DATE,
                              'call': 'self.localise(datetime.now()).date() + relativedelta(day=1, month=1)',
                              'arguments': [],
                              },
            'last_dow': {'type': java_odoo.TYPE_DATE,
                         'call': 'self.localise(datetime.now()).date() - relativedelta(days=7) + dow_offset(%1)',
                         'arguments': [{'types': (java_odoo.TYPE_STRING,),
                                        'lists': (False,),
                                        'insert_at': 1,
                                        'insert_as': 'dow_name'
                                        }],
                         },
            'next_dow': {'type': java_odoo.TYPE_DATE,
                         'call': 'self.localise(datetime.now()).date() + relativedelta(days=1) + dow_offset(%1)',
                         'arguments': [{'types': (java_odoo.TYPE_STRING,),
                                        'lists': (False,),
                                        'insert_at': 1,
                                        'insert_as': 'dow_name'
                                        }],
                         },

            'date_offset': {'type': FTYPE_TIMEDELTA,
                            'call': 'relativedelta(%1)',
                            'arguments': [{'name': 'years',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'months',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'weeks',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'days',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'hours',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'minutes',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'seconds',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          {'name': 'microseconds',
                                           'types': (java_odoo.TYPE_INTEGER, java_odoo.TYPE_NUMBER),
                                           'lists': (False,),
                                           'insert_at': 1,
                                           },
                                          ],
                            },
            'current_user': {'type': java_odoo.TYPE_INTEGER,
                             'call': 'self.env.uid',
                             'arguments': [],
                             }
            }


def dow_offset(dow_name=''):
    weekday=0
    if dow_name.lower() in ('monday', _('monday'), 'mon', 'mo', '0'):
        weekday=0
    if dow_name.lower() in ('tuesday', _('tuesday'), 'tues', 'tue', 'tu', '1'):
        weekday=1
    if dow_name.lower() in ('wednesday', _('wednesday'), 'wednes', 'wed', 'we', '2'):
        weekday=2
    if dow_name.lower() in ('thursday', _('thursday'), 'thurs', 'thu', 'th', '3'):
        weekday=3
    if dow_name.lower() in ('friday', _('friday'), 'fri', 'fr', '4'):
        weekday=4
    if dow_name.lower() in ('saturday', _('saturday'), 'satur', 'sat', 'sa', '5'):
        weekday=5
    if dow_name.lower() in ('sunday', _('sunday'), 'sun', 'su', '6'):
        weekday=6
    return relativedelta(weekday=weekday)
