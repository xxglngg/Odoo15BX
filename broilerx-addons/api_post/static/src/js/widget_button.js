odoo.define('odoo_javascript.my_widget', function (require) {
	var Widget= require('web.Widget');
	var widgetRegistry = require('web.widget_registry');
	var FieldManagerMixin = require('web.FieldManagerMixin');

	var MyWidget = Widget.extend(FieldManagerMixin, {
    init: function (parent, model, context) {
        this._super(parent);
        FieldManagerMixin.init.call(this);
		this._super.apply(this, arguments);
    },

    start: function() {
    	var self = this;
    	this._super.apply(this, arguments);
		var html ='<button id="check_api_post_use_json" class="btn btn-primary" style="font-size:8pt">CHECK API REQUEST USE JSON</button>';
		this.$el.html(html);
		this.$('#check_api_post_use_json').click(function(ev){
			console.log('DISINI MASUK');
            var ListController = require('web.ListController');
            var ListView = require('web.ListView');
            var viewRegistry = require('web.view_registry');
            var session = require('web.session');
            var rpc = require('web.rpc');

            var BasicFields = require('web.basic_fields');

            var core = require('web.core');
            var ajax = require('web.ajax');
            var ListRenderer = require("web.ListRenderer");
            var ajax = require('web.ajax');

            var rpc = require('web.rpc');

            var url = window.location.href;

            console.log(url);
            var myArrAmp = url.split("&");
            var myArrCrash = url.split("#");

            rpc.query({

                model: 'api.config',

                method: 'check_id_data',
                args: [{'array_amp':myArrAmp, 'array_crash':myArrCrash}],

            }).then(function(result){
                console.log('SUKSES FUNCTION RPC');
                console.log(result);
                var check_condition = result[0]['result'];
                console.log(check_condition);
                if(check_condition == 'true'){
                    var api = result[0]['api'];
                    var variable_filter = result[0]['variable_filter'];
                    console.log(api);
                    if(api == 'peternak'){
                        var id_api_config = result[0]['id'];
                        console.log('masuk peternak');
                        ajax.jsonRpc("/api_post_bx_15/json/peternak", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'customer'){
                        var id_api_config = result[0]['id'];
                        console.log(api);
                        console.log('masuk customer');
                        ajax.jsonRpc("/api_post_bx_15/json/customer", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'pakan pre-starter'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/pakan_pre_starter", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'pakan starter'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/pakan_starter", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'pakan finisher'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/pakan_finisher", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'doc'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/doc", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'ovk'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/ovk", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                    if(api == 'analytic_account'){
                        var id_api_config = result[0]['id'];
                        console.log(api);

                        ajax.jsonRpc("/api_post_bx_15/json/analytic_account", 'call', {'id':id_api_config,'variable_filter':variable_filter}).then(function (modal) {

                            alert('sukses');
                            window.location.reload();

                        });

                    }

                }else{
                    alert('JSON tidak ditemukan');
                }


            });
		});
    },
});

widgetRegistry.add(
    'my_widget', MyWidget
);

});

