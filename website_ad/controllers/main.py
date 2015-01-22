# -*- coding: utf-8 -*-
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

import re

from openerp.osv import fields


import logging
_logger = logging.getLogger(__name__)


#class Home2(http.Controller):
#    @http.route('/home2', type="http", auth="user")
#    def index(self):
#        return "<div>This is my new home page.</div>"
        
        
class website_order(http.Controller):

    @http.route(['/order/list',], type='http', auth="public", website=True)
#    @http.route(['/order/list',], type='http', auth="user", website=True)
    def order_list(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        res_user = request.registry.get('res.users').browse(cr,uid,uid)
        context['lang'] = res_user.lang

#        order_ids = request.registry.get('sale.order').search(cr,uid,[('company_id','=',res_user.company_id.id)],context=context)
        
#        partner_ids = request.registry.get('res.partner').search(cr,uid,[('company_id','=',res_user.company_id.id),('')],context=context)
#        partner_id
        
#        project_id
        
#       origin note client_order_ref name
#       origin note description name
        
        if post.get('search_phrase'):
            order_ids = request.registry.get('sale.order').search(cr,uid,[('company_id','=',res_user.company_id.id),'|',
                                                                                ('partner_id.name','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('partner_id.street','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('partner_id.city','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('project_id.name','ilike','%%%s%%' % post.get('search_phrase')),                                                            
#                                                                                ('client_order_ref','ilike','%%%s%%' % post.get('search_phrase')),
                                                                                ('description','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('origin','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('name','ilike','%%%s%%' % post.get('search_phrase')),
#                                                                                ('note','ilike','%%%s%%' % post.get('search_phrase'))
#            order_ids = request.registry.get('sale.order').search(cr,uid,[('partner_id.name','ilike','%%%s%%' % post.get('search_phrase')),
                                                                                
                                                                                
                                                                                ],context=context)
        else:
            order_ids = request.registry.get('sale.order').search(cr,uid,[('company_id','=',res_user.company_id.id)],context=context)
            
        values = {
            'context': context,
            'order_menu': 'active',
            'res_user': res_user,
            'form_action': '/order/list',
            'search_phrase': post.get('search_phrase'),
#            'sale_orders': request.registry.get('sale.order').browse(cr,uid,request.registry.get('sale.order').search(cr,uid,[('company_id','=',res_user.company_id.id)]),context=context),
            'sale_orders': request.registry.get('sale.order').browse(cr,uid,order_ids,context=context),
        }
        return request.website.render("smart_order.list",values)
        
    @http.route(['/order/list/all',], type='http', auth="user", website=True)
    def order_list_all(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        res_user = request.registry.get('res.users').browse(cr,uid,uid)
        context['lang'] = res_user.lang
        
        values = {
            'context': context,
            'order_all_menu': 'active',
            'res_user': res_user,
#            'sale_orders': request.registry.get('sale.order').browse(cr,uid,request.registry.get('sale.order').search(cr,uid,[('company_id','=',res_user.company_id.id)]),context=context),
            'sale_orders': request.registry['sale.order'].browse(cr, uid, request.registry['sale.order'].search(cr, uid,[]),context=context),

        }
        return request.website.render("smart_order.list_all",values)

#    @http.route(['/order/search',], type='http', auth="user", website=True)
#    def order_search(self, **post):
#        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#
#        res_user = request.registry.get('res.users').browse(cr,uid,uid)
#        context['lang'] = res_user.lang
#        
#        values = {
#            'context': context,
#            'order_menu': 'active',
#            'res_user': res_user,
#            'search_phrase': ['search_phrase'],
#            'sale_orders': request.registry.get('sale.order').browse(cr,uid,request.registry.get('sale.order').search(cr,uid,[('company_name','=','search_phrase')]),context=context),
#        }
#        return request.website.render("smart_order.list",values)


    @http.route(['/order/<model("sale.order"):sale_order>','/order/new','/order/<model("sale.order"):sale_order>/edit_lines','/order/<model("sale.order"):sale_order>/edit_order_data',
    '/order/<model("sale.order"):sale_order>/cancel/','/order/<model("sale.order"):sale_order>/line/<model("sale.order.line"):sale_order_line>/delete'], type='http', auth="user", website=True)
    def order(self, sale_order=False,sale_order_line=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        res_user = pool.get('res.users').browse(cr,uid,uid,context)
        context['lang'] = res_user.lang

        if not sale_order:
            template='smart_order.edit_order_data'
            context['next_form'] = 'smart_order.edit_lines'         
            context['form_action'] = '/order/new'
        else:
            template='smart_order.order'
            context['form_action'] = '/order/%s' % sale_order.id         
            if context.get('next_form') == 'smart_order.edit_order_data':
                template=context.get('next_form')     
            if context.get('next_form') == 'smart_order.edit_lines':
                template=context.get('next_form')
            if re.search("edit_lines",request.httprequest.url) is not None:
                template="smart_order.edit_lines"
            if re.search("edit_order_data",request.httprequest.url) is not None:
                template="smart_order.edit_order_data"
            if re.search("cancel",request.httprequest.url) is not None:
                sale_order.unlink()
                return werkzeug.utils.redirect('/order/list')
            if sale_order_line and re.search("delete",request.httprequest.url) is not None:
                sale_order_line.unlink()
                template="smart_order.edit_lines"



        analytic_ids = pool.get('account.analytic.account').search(cr,uid,['|',('company_id','=',False),('company_id','=',res_user.company_id.id)])                
        values = {
            'context': context,
            'order_menu': 'active',
            'res_user': res_user,
            'sale_order': sale_order,
            'context': context,
            'account_tax': pool.get('account.tax').browse(cr,uid,pool.get('account.tax').search(cr,uid,[('active_web','=',True)],context=context),context=context),
            'projects': pool.get('project.project').browse(cr,uid,pool.get('project.project').search(cr,uid,[('analytic_account_id','in',analytic_ids)],context=context),context=context),
            'clients_global':  request.registry['res.partner'].browse(cr,uid,request.registry['res.partner'].search(cr,uid,[('company_id','=',False)],context=context),context=context),
            'clients_order':  request.registry['res.partner'].browse(cr,uid,request.registry['res.partner'].search(cr,uid,['|',('company_id','=',False),('company_id','=',res_user.company_id.id)],context=context),context=context),
            'clients_local':  request.registry['res.partner'].browse(cr,uid,request.registry['res.partner'].search(cr,uid,[('company_id','=',res_user.company_id.id)],context=context),context=context),
        }

        if request.httprequest.method == 'POST':
            _logger.warning("This is order post %s /order/nn" % (post))

            if post.get('delete') == True:
                sale_order.unlink()
                return werkzeug.utils.redirect('/order/list')
                
            # Workflow from sale.order
            for signal in [transition.signal for transition in request.registry['workflow.transition'].browse(cr,uid,request.registry['workflow.transition'].search(cr,uid,[('signal','>','')])) if post.get(transition.signal)]:

#            work_flow = [for wf in ['quo','cancel2','cancel3','done','draft','invoice','invoice_cancel','invoice_end','invoice_except','router','sent','ship','ship_cancel','ship_cancel','ship_end','ship_except','ship_ignore','wait_invoice','wait_ship'] if post.get(wf))]
#            work_flow = ()
#            if len(work_flow)>0:
                try:
                    request.session.exec_workflow('sale.order', sale_order.id, signal)
                except Exception, ex: 
                    values['error'] = "Error: %s" % ex
                return werkzeug.utils.redirect('/order/list')

            if post.get('paid') == True:
                request.session.exec_workflow('sale.order', sale_order.id, 'order_paid')
                values['sale_order']= request.registry.get('sale.order').browse(cr,uid,sale_order.id)
                return request.website.render(template, values)

            if post.get('partner_id') and pool.get('res.partner').search(cr,uid,[('id','=',post.get('partner_id'))],context=context):
                partner_id = pool.get('res.partner').search(cr,uid,[('id','=',post.get('partner_id'))],context=context)
                partner = pool.get('res.partner').browse(cr,uid,partner_id,context=context)
                partner_addr = partner.address_get(['default', 'invoice', 'delivery', 'contact'])

                if not sale_order:
                    sale_order_id = pool.get('sale.order').create(cr,uid,{
                        'origin': _('Front order'),
                        'partner_id': partner.id,
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,   
                        'payment_term': partner.property_payment_term and partner.property_payment_term.id or False,
                        'partner_invoice_id': partner_addr['invoice'],
                        'partner_shipping_id': partner_addr['delivery'],
#                        'date_order': fields.date.context_today(self,cr,uid,context=context),
                        'pricelist_id': partner.property_product_pricelist.id,
                    })
                    sale_order = pool.get('sale.order').browse(cr,uid,sale_order_id)
                    template='smart_order.edit_lines'
                    context['form_action'] = '/order/%s' % sale_order.id
                
                sale_order.write({'partner_id': partner.id})

            if not sale_order:
                values['error'] = _('Something went wrong with the form (no sale_order)')
                return request.website.render(template, values)

            if post.get('project_id'):
                sale_order.write({'project_id': post.get('project_id')})
#            if post.get('client_order_ref'):
#                sale_order.write({'client_order_ref': post.get('client_order_ref')})
            if post.get('description'):
                sale_order.write({'description': post.get('description')})


## Sale Order Lines
            if post.get('line_name_new'):
                    pool.get('sale.order.line').create(cr,uid,{'order_id': sale_order.id, 'name': post.get('line_name_new'), 'price_unit': float(post.get('line_price_new')), 'product_uom_qty': 1.0, 'tax_id': [(6,0,[post.get('line_tax_new',1)])] })
                    template='smart_order.edit_lines'
#Anders: H�r vill jag att Save-Order-Line landar p� smart_order.edit_lines och att Next landar p� smart_order.order
                    values['form_action'] = '/order/%s' % sale_order.id
            else:
                for line in post.keys():
                    if line.startswith('line_id_'):
                        r = re.match("line_id_(\d+)",line)
                        row = str(r.groups(1)[0])
                        order_line = pool.get('sale.order.line').browse(cr,uid,int(post.get('line_id_' + row)),context=context)
                        order_line.write({'name': post.get('line_name_' + row), 'price_unit': float(post.get('line_price_' + row)), 'product_uom_qty': 1.0, 'tax_id': [(6,0,[post.get('line_tax_' + row,1)])]})
#                        order_line.write({'name': post.get('line_name_' + row), 'price_unit': float(post.get('line_price_' + row)), 'product_uom_qty': float(post.get('line_qty_' + row)), 'vat': post.get('line_vat_' + row)})

            values['sale_order']= pool.get('sale.order').browse(cr,uid,sale_order.id)

## Return to the form
            if post.get('redirect'):
                return werkzeug.utils.redirect(post.get('redirect'))
            else:
                return request.website.render(template, values)

        else:  # Not POST
            if not sale_order:
                return request.website.render(template, values)
            elif sale_order.company_id.id <> res_user.company_id.id:
                values['error'] = 'Not authorized to view this order'
            return request.website.render(template, values)


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
