odoo.define('custom_import_template.import', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var BaseImport = require('base_import.import');
    var action_registry = core.action_registry.get('import');
    var QWeb = core.qweb;
    
    action_registry.include({
        _DownloadImportTemplate: function (event) {
            var self = this;
            if (self.res_model == 'purchase.order'){
                self._rpc({
                    model: 'base_import.import',
                    method: 'download_template_purchase',
                }).then(function(action){
                return self.do_action(action);
                });
            }
            if (self.res_model == 'sale.order'){
                self._rpc({
                    model: 'base_import.import',
                    method: 'download_template_sale',
                }).then(function(action){
                return self.do_action(action);
                });
            }
        },
        renderButtons: function() {
            var self = this;
            this.$buttons = $(QWeb.render("ImportView.buttons", this));
            this.$buttons.filter('.o_import_validate').on('click', this.validate.bind(this));
            this.$buttons.filter('.o_import_import').on('click', this.import.bind(this));
            this.$buttons.filter('.oe_import_file').on('click', function () {
                self.$('.o_content .oe_import_file').click();
            });
            this.$buttons.filter('.o_import_cancel').on('click', function(e) {
                e.preventDefault();
                self.exit();
            });
            if (this.res_model == 'purchase.order' || this.res_model == 'sale.order'){
                this.$buttons.filter('.o_import_template').on('click', this._DownloadImportTemplate.bind(this));
            }
        },
    });

});