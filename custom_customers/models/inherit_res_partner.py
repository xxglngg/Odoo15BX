# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

REGION_SELECTION = [
    ('jateng', 'Jateng & DIY'),
    ('jatim', 'Jatim'),
    ('lampung', 'Lampung'),
    ('bali', 'Bali Nusa'),
    ('kaltim', 'Kaltim'),
]

PRODUCT_SELECTION = [
    ('pakan', 'Pakan'),
    ('doc', 'DOC'),
    ('ovk', 'OVK'),
]

class ContactProduct(models.Model):
    _name = 'contact.product'
    _description = 'Contact Product'

    name = fields.Char(string="Name")

class InheritModelResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Inherit Model Res Partner'
    
    upload_ktp = fields.Binary(string="Upload KTP")
    file_ktp = fields.Char(string="File KTP")
    upload_npwp = fields.Binary(string="Upload NPWP")
    file_npwp = fields.Char(string="File NPWP")
    upload_rekening = fields.Binary(string="Upload Rekening")
    file_rekening = fields.Char(string="File Rekening")
    segmentasi_id = fields.Many2one('res.partner.segmentasi', string="Segmentasi")
    salesman_id = fields.Many2one('res.partner', string="Salesman")
    code_salesman = fields.Char(string="Code Salesman")
    last_sequence = fields.Char('Last Sequence', readonly=True, select=True, copy=False, default='New')
    is_salesman = fields.Boolean('Is Salesman', compute="_compute_is_salesman", store=True)
    supplier_rank = fields.Integer(default=0)
    customer_rank = fields.Integer(default=0)
    is_company_pis = fields.Boolean('Is Company PIS', compute="_compute_is_company_pis")
    contact_name = fields.Char(string='Contact Name')
    contact_region = fields.Selection(REGION_SELECTION, string="Wilayah", default='')
    contact_product_ids = fields.Many2many('contact.product', string="Product")
    is_vendor = fields.Boolean('Is Vendor', compute="_compute_is_vendor", store=True)
    is_ref = fields.Boolean('Is Reference', compute="_compute_is_ref", store=True)
    is_company_itu = fields.Boolean('Is Company ITU', compute="_compute_is_company_itu", store=True)
    vat = fields.Char(string="NPWP", size=16)

    @api.constrains('vat')
    def _check_vat_length(self):
        for record in self:
            if record.vat:
                if len(record.vat) < 15 or not record.vat.isdigit():
                    raise ValidationError("NPWP less than 15 or 16 digits long and contain only numbers.")
    
    @api.depends('company_id')
    def _compute_is_company_itu(self):
        for rec in self:
            rec.is_company_itu = False
            if rec.company_id.name == 'PT Integrasi Teknologi Unggas':
                rec.is_company_itu = True

    @api.onchange('vat')
    def _onchange_id_pkp(self):
        for rec in self:
            rec.l10n_id_pkp = False
            if rec.vat:
                rec.l10n_id_pkp = True

    @api.depends('category_id')
    def _compute_is_ref(self):
        for rec in self:
            rec.is_ref = True
            if rec.category_id:
                for categ in rec.category_id:
                    if categ.name == 'customer':
                        rec.is_ref = False
                    if categ.name == 'Vendor':
                        rec.is_ref = False
                    
    @api.onchange('ref','contact_name','contact_region','contact_product_ids')
    def _onchange_is_vendor(self):
        for rec in self:
            if rec.is_vendor == True:
                if rec.contact_name and rec.contact_region and rec.contact_product_ids:
                    total_product = []
                    contact_region_string = dict(self._fields['contact_region'].selection).get(self.contact_region)
                    for product in rec.contact_product_ids:
                        total_product.append(product.name)
                        contact_product_string = ', '.join(total_product)
                        rec.name = rec.contact_name+' - '+contact_region_string+' - '+contact_product_string
                else:
                    rec.name = rec.contact_name
            else:
                if rec.ref and rec.contact_name:
                    rec.name = rec.ref+' - '+rec.contact_name
                else:
                    rec.name = rec.contact_name

    @api.depends('category_id')
    def _compute_is_vendor(self):
        for rec in self:
            rec.is_vendor = False
            if rec.category_id:
                for categ in rec.category_id:
                    if categ.name == 'Vendor':
                        rec.is_vendor = True

    @api.depends('customer_rank')
    def _compute_is_company_pis(self):
        for rec in self:
            rec.is_company_pis = False
            if rec.customer_rank > 0:
                if self.env.company.name == 'PT Pangan Integrasi Sejahtera':
                    rec.is_company_pis = True

    @api.depends('category_id')
    def _compute_is_salesman(self):
        for rec in self:
            rec.is_salesman = False
            if rec.category_id:
               for categ in rec.category_id:
                   if categ.name == 'Salesman':
                       rec.is_salesman = True 

    @api.model
    def default_get(self, fields):
        res = super(InheritModelResPartner, self).default_get(fields)
        if res.get('customer_rank'):
            if res.get('customer_rank') > 0:
                customers = self.env['res.partner.category'].search([('name', '=', 'customer')])
                res.update({
                    'category_id': customers
                })
        if res.get('supplier_rank'):
            if res.get('supplier_rank') > 0:
                vendors = self.env['res.partner.category'].search([('name', '=', 'Vendor')])
                res.update({
                    'category_id': vendors
                })
        return res

    @api.model
    def create(self, vals):
        if vals.get('parent_id'):
            parent = self.env['res.partner'].search([('id', '=', vals.get('parent_id'))])
            category_id = []
            if parent.category_id:
                for category in parent:
                    category_id.append([6, False, [category.category_id.id]])
                vals['category_id'] = category_id
        if vals.get('last_sequence', 'New') == 'New':
            if vals.get('customer_rank'):
                if vals.get('customer_rank') > 0 and self.env.company.name == 'PT Pangan Integrasi Sejahtera':
                    if not vals.get('is_salesman'):
                        code_segment = self.env['res.partner.segmentasi'].search([('id', '=', vals.get('segmentasi_id'))]).code
                        code_sales = self.env['res.partner'].search([('id', '=', vals.get('salesman_id'))]).code_salesman
                        vals['last_sequence'] = self.env['ir.sequence'].next_by_code('res.code.partner') or 'New'
                        vals['ref'] = 'C/'+code_segment+'/'+code_sales+'/'+vals['last_sequence']
        result = super(InheritModelResPartner, self).create(vals)
        return result

    def action_view_image_ktp(self):
        if self.file_ktp.endswith('.png') or self.file_ktp.endswith('.jpg') or self.file_ktp.endswith('.jpeg'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_ktp': self.upload_ktp,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_image_ktp'
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
        
        if self.file_ktp.endswith('.pdf'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_ktp': self.upload_ktp,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_pdf_ktp'
            )

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
    
    def action_view_image_npwp(self):
        if self.file_npwp.endswith('.png') or self.file_npwp.endswith('.jpg') or self.file_npwp.endswith('.jpeg'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_npwp': self.upload_npwp,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_image_npwp'
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
        
        if self.file_npwp.endswith('.pdf'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_npwp': self.upload_npwp,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_pdf_npwp'
            )

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
    
    def action_view_image_rekening(self):
        if self.file_rekening.endswith('.png') or self.file_rekening.endswith('.jpg') or self.file_rekening.endswith('.jpeg'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_rekening': self.upload_rekening,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_image_rekening'
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }
        
        if self.file_rekening.endswith('.pdf'):
            id = self.id

            context = {
                'default_id': id,
                'default_upload_rekening': self.upload_rekening,
            }

            compose_form = self.env.ref(
                'custom_customers.wizard_view_pdf_rekening'
            )

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'context': context,
                'nodestroy': True,
                'target': 'new',
                'res_id':id,
            }

    @api.constrains('phone')
    def check_phone_customers(self):
        for rec in self:
            if rec.phone:
                duplicate_partners = self.env['res.partner'].search([('phone', '=', rec.phone),('id', '!=', rec.id)])
                if duplicate_partners:
                    if len(duplicate_partners) > 1:
                        name = ', '.join([dp.name for dp in duplicate_partners])
                        raise ValidationError(_('Nomor telefon yang anda masukkan %s, sudah digunakan pada kontak %s') % (duplicate_partners[0].phone, name))
                    else:
                        raise ValidationError(_('Nomor telefon yang anda masukkan %s, sudah digunakan pada kontak %s') % (duplicate_partners.phone, duplicate_partners.name))