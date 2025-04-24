from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError, UserError

class AnalyticRhppJournalWizard(models.TransientModel):
    _name = 'analytic.rhpp.journal.wizard'
    _description = 'Analytic RHPP Journal Wizard'
    
    def confirm_journal_change(self):
        analytic_rhpp =  self.env['analytic.rhpp'].search([('id', '=', self.env.context.get('active_id'))])
        account_move = self.env['account.move'].search([('analytic_rhpp_id', '=', analytic_rhpp.id), ('state', '=', 'draft')], limit=1)
        if not account_move:
            raise ValidationError('Check journal entry state draft')
        account_move.line_ids.unlink()
        journal = self.env['account.journal'].search([('name', '=', 'Jurnal Umum'), ('company_id', '=', self.env.company.id)], limit=1)
        if not journal:
            raise ValidationError('Jurnal Umum Not Exists, please contact admin for create account journal')
        profit_loss = analytic_rhpp.live_bird - (analytic_rhpp.doc + analytic_rhpp.pakan + analytic_rhpp.obat_vaksin_kimia + analytic_rhpp.iot)
        if profit_loss > 0:
            try:
                penjualan_debit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                
            try:
                penjualan_credit = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                
            try:
                pembelian_debit = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
            
            try:
                pembelian_credit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
            
            try:
                pendapatan_awal = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
            
            try:
                biaya_produksi = self.env['account.account'].search([('code', '=', '5150001102')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (5150001102)'))
                
            try:
                pph21 = self.env['account.account'].search([('code', '=', '2160001103')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2160001103)'))
                
            try:
                utang_titipan = self.env['account.account'].search([('code', '=', '2180001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2180001101)'))
                
            try:
                utang_rhpp = self.env['account.account'].search([('code', '=', '2180001102')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2180001102)'))
            tabungan_peternak = 0
            if analytic_rhpp.pendapatan_ratio > 3000:
                tabungan_peternak = (analytic_rhpp.pendapatan_awal+analytic_rhpp.bonus_ch+analytic_rhpp.bonus_ip+analytic_rhpp.bonus_capaian_fcr+analytic_rhpp.bonus_daya_hidup+analytic_rhpp.kompensasi) * 0.10    
            move = {
                'line_ids': [
                                (0, 0, {
                                        'name': 'Penjualan',
                                        'debit': analytic_rhpp.sale,
                                        'account_id': penjualan_debit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                        }
                                ), 
                                (0, 0, {
                                        'name': 'Penjualan',
                                        'credit': analytic_rhpp.sale,
                                        'account_id': penjualan_credit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pembelian Livebird',
                                        'debit': analytic_rhpp.live_bird,
                                        'account_id': pembelian_debit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pembelian Livebird',
                                        'credit': analytic_rhpp.live_bird,
                                        'account_id': pembelian_credit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pendapatan Awal',
                                        'debit': analytic_rhpp.pendapatan_awal,
                                        'account_id': pendapatan_awal,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Kompensasi',
                                        'debit': analytic_rhpp.kompensasi,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Bonus CH',
                                        'debit': analytic_rhpp.bonus_ch,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Bonus IP',
                                        'debit': analytic_rhpp.bonus_ip,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Bonus Pasar',
                                        'debit': analytic_rhpp.bonus_pasar,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Bonus Capaian FCR',
                                        'debit': analytic_rhpp.bonus_capaian_fcr,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Bonus Daya Hidup',
                                        'debit': analytic_rhpp.bonus_daya_hidup,
                                        'account_id': biaya_produksi,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'PPh Ps 21',
                                        'credit': analytic_rhpp.pph_21,
                                        'account_id': pph21,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Tabungan Peternak',
                                        'credit': tabungan_peternak,
                                        'account_id': utang_titipan,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pencairan RHPP',
                                        'credit': (analytic_rhpp.pendapatan_awal+analytic_rhpp.bonus_ch+analytic_rhpp.bonus_ip+analytic_rhpp.bonus_capaian_fcr+analytic_rhpp.bonus_daya_hidup+analytic_rhpp.kompensasi)-(analytic_rhpp.pph_21 + tabungan_peternak),
                                        'account_id': utang_rhpp,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                })
                            ] 
            }
            account_move.write(move)
        else:
            try:
                penjualan_debit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
                
            try:
                penjualan_credit = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                
            try:
                pembelian_debit = self.env['account.account'].search([('code', '=', '2110001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (2110001101)'))
            
            try:
                pembelian_credit = self.env['account.account'].search([('code', '=', '1130001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1130001101)'))
            
            try:
                pendapatan_awal = self.env['account.account'].search([('code', '=', '1140001101')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (1140001101)'))
                
            try:
                biaya_produksi_rhpp = self.env['account.account'].search([('code', '=', '5150001102')], limit=1).id
            except:
                raise ValidationError(_('Chart Of Account Does Not Exists, code number (5150001102)'))
                
            move = {
                'line_ids': [
                                (0, 0, {
                                        'name': 'Penjualan',
                                        'debit': analytic_rhpp.sale,
                                        'account_id': penjualan_debit,
                                        'partner_id': analytic_rhpp.name.id
                                        }
                                ), 
                                (0, 0, {
                                        'name': 'Penjualan',
                                        'credit': analytic_rhpp.sale,
                                        'account_id': penjualan_credit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pembelian Livebird',
                                        'debit': analytic_rhpp.live_bird,
                                        'account_id': pembelian_debit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pembelian Livebird',
                                        'credit': analytic_rhpp.live_bird,
                                        'account_id': pembelian_credit,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Pendapatan Awal',
                                        'credit': analytic_rhpp.pendapatan_awal,
                                        'account_id': pendapatan_awal,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                }), 
                                (0, 0, {
                                        'name': 'Sisa AR',
                                        'debit': analytic_rhpp.pendapatan_awal,
                                        'account_id': biaya_produksi_rhpp,
                                        'analytic_account_id': analytic_rhpp.id_mitra.id,
                                        'partner_id': analytic_rhpp.name.id
                                })
                            ] 
            }
            account_move.write(move)
        analytic_rhpp.state = 'finance'
        return {'type': 'ir.actions.act_window_close'}