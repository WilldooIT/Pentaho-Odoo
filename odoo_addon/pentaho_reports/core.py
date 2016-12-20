# -*- encoding: utf-8 -*-
# Todo:
#    multiple prpt files for one action - allows for alternate formats.

import xmlrpclib
import base64

from odoo.report.interface import report_int
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config
import logging
import time
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

from .java_odoo import JAVA_MAPPING, check_java_list, PARAM_VALUES, RESERVED_PARAMS

_logger = logging.getLogger(__name__)

SERVICE_NAME_PREFIX = 'report.'
VALID_OUTPUT_TYPES = [('pdf', 'Portable Document (pdf)'),
                      ('xls', 'Excel Spreadsheet (xls)'),
                      ('xlsx', 'Excel 2007 Spreadsheet (xlsx)'),
                      ('csv', 'Comma Separated Values (csv)'),
                      ('rtf', 'Rich Text (rtf)'),
                      ('html', 'HyperText (html)'),
                      ('txt', 'Plain Text (txt)'),
                      ]
DEFAULT_OUTPUT_TYPE = 'pdf'

def get_date_length(date_format=DEFAULT_SERVER_DATE_FORMAT):
    return len((datetime.now()).strftime(date_format))

class _format(object):

    def set_value(self, cr, uid, name, object, field, lang_obj):
        self.object = object
        self._field = field
        self.name = name
        self.lang_obj = lang_obj

class _float_format(float, _format):
    def __init__(self, value):
        super(_float_format, self).__init__()
        self.val = value or 0.0

    def __str__(self):
        digits = 2
        if hasattr(self, '_field') and getattr(self._field, 'digits', None):
            digits = self._field.digits[1]
        if hasattr(self, 'lang_obj'):
            return self.lang_obj.format('%.' + str(digits) + 'f', self.name, True)
        return str(self.val)

class _int_format(int, _format):
    def __init__(self, value):
        super(_int_format, self).__init__()
        self.val = value or 0

    def __str__(self):
        if hasattr(self, 'lang_obj'):
            return self.lang_obj.format('%.d', self.name, True)
        return str(self.val)

class _date_format(str, _format):
    def __init__(self, value):
        super(_date_format, self).__init__()
        self.val = value and str(value) or ''

    def __str__(self):
        if self.val:
            if getattr(self, 'name', None):
                date = datetime.strptime(self.name[:get_date_length()], DEFAULT_SERVER_DATE_FORMAT)
                return date.strftime(str(self.lang_obj.date_format))
        return self.val

class _dttime_format(str, _format):
    def __init__(self, value):
        super(_dttime_format, self).__init__()
        self.val = value and str(value) or ''

    def __str__(self):
        if self.val and getattr(self, 'name', None):
            return datetime.strptime(self.name, DEFAULT_SERVER_DATETIME_FORMAT)\
                   .strftime("%s %s" % (str(self.lang_obj.date_format),
                                      str(self.lang_obj.time_format)))
        return self.val

class browse_record_list(list):
    def __init__(self, lst, context):
        super(browse_record_list, self).__init__(lst)
        self.context = context

    def __getattr__(self, name):
        res = browse_record_list([getattr(x, name) for x in self], self.context)
        return res

    def __str__(self):
        return "browse_record_list(" + str(len(self)) + ")"

_fields_process = {
        'float': _float_format,
        'date': _date_format,
        'integer': _int_format,
        'datetime': _dttime_format
    }

def get_proxy_args(instance, cr, uid, prpt_content, context_vars={}):
    """Return the arguments needed by Pentaho server proxy.

    @return: Tuple with:
        [0]: Has the url for the Pentaho server.
        [1]: Has dict with basic arguments to pass to Pentaho server. This
             includes the connection settings and report definition, as well
             as reserved parameters evaluated according to values in
             the dictionary "context_vars".
    """
    env = api.Environment(cr, uid, {})

    current_user = env['res.users'].browse(uid)
    IRConfig = env['ir.config_parameter']

    proxy_url = IRConfig.get_param('pentaho.server.url', default='http://localhost:8080/pentaho-reports-for-odoo')

    xml_interface = IRConfig.get_param('pentaho.odoo.xml.interface', default='').strip() or config['xmlrpc_interface'] or 'localhost'
    xml_port = IRConfig.get_param('pentaho.odoo.xml.port', default='').strip() or str(config['xmlrpc_port'])

    password_to_use = env['res.users'].browse(uid).pentaho_pass_token()

    proxy_argument = {
                      'prpt_file_content': xmlrpclib.Binary(prpt_content),
                      'connection_settings': {'odoo': {'host': xml_interface,
                                                       'port': xml_port,
                                                       'db': cr.dbname,
                                                       'login': current_user.login,
                                                       'password': password_to_use,
                                                       },
                                              },
                      'report_parameters': dict([(param_name, param_formula(instance, cr, uid, context_vars)) for (param_name, param_formula) in RESERVED_PARAMS.iteritems() if param_formula(instance, cr, uid, context_vars)]),
                      }

    postgresconfig_host = IRConfig.get_param('pentaho.postgres.host', default='localhost')
    postgresconfig_port = IRConfig.get_param('pentaho.postgres.port', default='5432')
    postgresconfig_login = IRConfig.get_param('pentaho.postgres.login')
    postgresconfig_password = IRConfig.get_param('pentaho.postgres.password')

    if postgresconfig_host and postgresconfig_port and postgresconfig_login and postgresconfig_password:
        proxy_argument['connection_settings'].update({'postgres': {'host': postgresconfig_host,
                                                                   'port': postgresconfig_port,
                                                                   'db': cr.dbname,
                                                                   'login': postgresconfig_login,
                                                                   'password': postgresconfig_password,
                                                                   }})

    return proxy_url, proxy_argument

def clean_proxy_args(instance, cr, uid, prpt_content, proxy_argument):
    env = api.Environment(cr, uid, {})
    env['res.users'].browse(uid).pentaho_undo_token(proxy_argument.get('connection_settings',{}).get('odoo',{}).get('password',''))

class Report(object):
    def __init__(self, name, cr, uid, ids, data, context):
        env = api.Environment(cr, uid, context)
        user = env['res.users'].browse(uid)

        self.name = name
        self.cr = cr
        self.uid = uid
        self.ids = ids
        self.data = data
        self.context = context or {}
        self.prpt_content = None
        self.default_output_type = DEFAULT_OUTPUT_TYPE
        self.context_vars = {
                             'ids': self.ids,
                             'uid': self.uid,
                             'context': self.context,
                             'user': user,
                             #
#                              'lang' : user.company_id.partner_id.lang,
                             }
#         self.setCompany(user.company_id)
#         self._lang_cache = {}
#         self.lang_dict = {}
#         self.default_lang = {}
#         self.lang_dict_called = False

    def setup_report(self):
        env = api.Environment(self.cr, self.uid, {})
        report = env['ir.actions.report.xml'].search([('report_name', '=', self.name[len(SERVICE_NAME_PREFIX):]), ('report_type', '=', 'pentaho')], limit=1)
        if not report:
            raise ValidationError(_("Report service name '%s' is not a Pentaho report.") % self.name[len(SERVICE_NAME_PREFIX):])
        self.default_output_type = report.pentaho_report_output_type or DEFAULT_OUTPUT_TYPE
        self.prpt_content = base64.decodestring(report.pentaho_file)

    def execute(self):
        self.setup_report()
        # returns report and format
        return self.execute_report()

    def fetch_report_parameters(self):
        """Return the parameters object for this report.

        Returns the parameters object as returned by the Pentaho
        server.
        """
        self.setup_report()

        proxy_url, proxy_argument = get_proxy_args(self, self.cr, self.uid, self.prpt_content, self.context_vars)
        proxy = xmlrpclib.ServerProxy(proxy_url)
        result = proxy.report.getParameterInfo(proxy_argument)

        clean_proxy_args(self, self.cr, self.uid, self.prpt_content, proxy_argument)
        return result

    def execute_report(self):
        proxy_url, proxy_argument = get_proxy_args(self, self.cr, self.uid, self.prpt_content, self.context_vars)
        proxy = xmlrpclib.ServerProxy(proxy_url)
        proxy_parameter_info = proxy.report.getParameterInfo(proxy_argument)

        output_type = self.data and self.data.get('output_type', False) or self.default_output_type or DEFAULT_OUTPUT_TYPE
        proxy_argument['output_type'] = output_type

        if self.data and self.data.get('variables', False):
            proxy_argument['report_parameters'].update(self.data['variables'])
            for parameter in proxy_parameter_info:
                if parameter['name'] in proxy_argument['report_parameters'].keys():
                    value_type = parameter['value_type']
                    java_list, value_type = check_java_list(value_type)
                    if not value_type == 'java.lang.Object' and PARAM_VALUES[JAVA_MAPPING[value_type](parameter['attributes'].get('data-format', False))].get('convert', False):
                        # convert from string types to correct types for reporter
                        proxy_argument['report_parameters'][parameter['name']] = PARAM_VALUES[JAVA_MAPPING[value_type](parameter['attributes'].get('data-format', False))]['convert'](proxy_argument['report_parameters'][parameter['name']])
                    # turn in to list
                    if java_list and type(proxy_argument['report_parameters'][parameter['name']]) != list:
                        proxy_argument['report_parameters'][parameter['name']] = [proxy_argument['report_parameters'][parameter['name']]]

        rendered_report = proxy.report.execute(proxy_argument).data
        clean_proxy_args(self, self.cr, self.uid, self.prpt_content, proxy_argument)

        if len(rendered_report) == 0:
            raise ValidationError(_("Pentaho returned no data for the report '%s'. Check report definition and parameters.") % self.name[len(SERVICE_NAME_PREFIX):])

        return (rendered_report, output_type)


class PentahoReportOdooInterface(report_int):
    def __init__(self, name):
        super(PentahoReportOdooInterface, self).__init__(name)

    def create(self, cr, uid, ids, data, context):
        name = self.name
        env = api.Environment(cr, uid, context)

        report_xml = env['ir.actions.report.xml'].search([('report_name', '=', name[len(SERVICE_NAME_PREFIX):])], limit=1)
        if report_xml and report_xml.attachment:
            for id in ids:
                report_instance = Report(name, cr, uid, [id], data, context)
                rendered_report, output_type = report_instance.execute()
                self.create_attachment(cr, uid, [id], report_xml.attachment, rendered_report, output_type, report_xml.pentaho_report_model_id.model, context=context)
            if len(ids) == 1:
                # If only one, do not need to re-run
                return rendered_report, output_type

        report_instance = Report(name, cr, uid, ids, data, context)
        rendered_report, output_type = report_instance.execute()
        return rendered_report, output_type

#     def getObjects(self, cr, uid, ids, model, context):
#         env = api.Environment(cr, uid, context or {})
#         return env[model].browse(ids)

    def create_attachment(self, cr, uid, ids, attachment, rendered_report, output_type, model, context):
        """Generates attachment when report is called and links to object it is called from
        Returns: True """
        env = api.Environment(cr, uid, context or {})
        objs = env[model].browse(ids)
        IRAttachment=env['ir.attachment']
        for obj in objs:
            attachments = IRAttachment.search([('res_id', '=', obj.id), ('res_model', '=', model)])
            aname = eval(attachment, {'object': obj, 'version': str(len(attachments)), 'time': time.strftime('%Y-%m-%d')})
            if aname:
                try:
                    name = '%s%s' % (aname, '' if aname.endswith(output_type) else '.' + output_type)
                    # Remove the default_type entry from the context: this
                    # is for instance used on the account.account_invoices
                    # and is thus not intended for the ir.attachment type
                    # field.
                    ctx = dict(context)
                    ctx.pop('default_type', None)
                    IRAttachment.create({
                                         'name': name,
                                         'datas': base64.encodestring(rendered_report),
                                         'datas_fname': name,
                                         'res_model': model,
                                         'res_name': aname,
                                         'res_id': obj.id,
                                         },
                    )
                except Exception:
                    #TODO: should probably raise a proper osv_except instead, shouldn't we? see LP bug #325632
                    _logger.error('Could not create saved report attachment', exc_info=True)
        return True

def check_report_name(report_name):
    """Adds 'report.' prefix to report name if not present already
    Returns: full report name
    """
    if not report_name.startswith(SERVICE_NAME_PREFIX):
        name = "%s%s" % (SERVICE_NAME_PREFIX, report_name)
    else:
        name = report_name
    return name

def fetch_report_parameters(cr, uid, report_name, context=None):
    """Return the parameters object for this report.

    Returns the parameters object as returned by the Pentaho
    server.

    @param report_name: The service name for the report.
    """
    name = check_report_name(report_name)
    return Report(name, cr, uid, [1], {}, context).fetch_report_parameters()

class ReportXML(models.Model):
    _inherit = 'ir.actions.report.xml'

    @api.model_cr
    def _lookup_report(self, name):
        self.env.cr.execute("SELECT * FROM ir_act_report_xml WHERE report_name=%s and report_type=%s", (name, 'pentaho'))
        r = self.env.cr.dictfetchone()
        if r:
            return PentahoReportOdooInterface(SERVICE_NAME_PREFIX+r['report_name'])
        return super(ReportXML, self)._lookup_report(name)

