// bi_survey_customization js
odoo.define('bi_survey_files_upload.survey', function(require) {
    "use strict";

    var form = require('survey.form');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
	var SurveyFormWidget = publicWidget.registry.SurveyFormWidget;
    var _t = core._t;
    
	console.log("Key..............$$$$$kkkkkkkkkkkppp",SurveyFormWidget)
    // Load form

	SurveyFormWidget.include({


		_prepareSubmitValues: function (formData, params) {
            var self = this;
            console.log("==============", self)
            formData.forEach(function (value, key) {
                switch (key) {
                    case 'csrf_token':
                    case 'token':
                    case 'page_id':
                    case 'question_id':
                        params[key] = value;
                        break;
                }
            });

            this.$('[data-question-type]').each(function () {
                switch ($(this).data('questionType')) {
                    case 'text_box':
                    case 'char_box':
                    case 'numerical_box':
                        params[this.name] = this.value;
                        break;
                    case 'date':
                        params = self._prepareSubmitDates(params, this.name, this.value, false);
                        break;
                    case 'datetime':
                        params = self._prepareSubmitDates(params, this.name, this.value, true);
                        break;
                    case 'simple_choice_radio':
                    case 'multiple_choice':
                        params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                        break;
                    case 'matrix':
                        params = self._prepareSubmitAnswersMatrix(params, $(this));
                        break;
                    case 'upload_file':
                        var attach_count = this.files.length;
                        var upload_files = [];
                        var final = [];
                        for(let i=0;i<attach_count;i++){
                            let file = this.files[i];
                            final.push($(this).parent().find('.image_data_div').find('.img_data_'+i).val());
                        }
                        params[this.name] = final;
                        break;
                }
            });
        },

	});
});



function get_attachment_data(ev){
    var self = ev;
    // var $i = $('#all_attachment'),
    //     input = $i[0];
    var attach_count = ev.files.length;
    var upload_files = [];
    var ok1 = ev.getAttribute('is-multi-file')
    console.log(attach_count,ev,"ok1------------------",ok1,$(ev))
    for(let i=0;i<attach_count;i++){
        let file = ev.files[i];
        $(ev).parent().find('.image_data_div').empty();
        let fr = new FileReader();
        fr.onload = function (file){
            let data = fr.result;
            data = data.split(',')[1];
            let vals = {
                name: self.files[i].name,
                type: self.files[i].type,
                data : data,
            };
            console.log("calling...........",vals)
            upload_files.push(vals);
            let img_name = 'img_data_'+ i.toString();
            let view = `<textarea  name="`+img_name+`"   class="`+img_name+`" 
                style="display: none;" >`+JSON.stringify(vals);+`</textarea>`;
            $(ev).parent().find('.image_data_div').append(view);
        };
        fr.readAsDataURL(file);
    }


    if (ok1 == 'True'){
        //$(ev).parent().find(".bi_attachment_lbl").hide()
        //$(ev).parent().find(".bi_attachment_lbl_multi").hide()
        var attach_count_ok = ev.files.length;
        $(ev).parent().find('#attach-name-multi').empty();
        //ev.refresh();
        console.log("mmmm", $(ev).parent())
        for(var i=0;i<attach_count_ok;i++){
            $(ev).parent().find('#attach-name-multi').append(ev.files[i].name)
            if(i!=(attach_count_ok -1)){
                $(ev).parent().find('#attach-name-multi').append(','+' ')
            }
        }
    }

    else {
    //$(ev).parent().find(".bi_attachment_lbl_multi").hide()
    //$(ev).parent().find(".bi_attachment_lbl").hide()
    var attach_count_ok = ev.files.length;
    console.log("NNNNNN", $(ev).parent())
    $(ev).parent().find("#attach-name").empty();
    for(var i=0;i<attach_count_ok;i++){
        $(ev).parent().find("#attach-name").append(ev.files[i].name)
        if(i!=(attach_count_ok -1)){
            $(ev).parent().find("#attach-name").append(','+' ')
        }
    }}
    $('.custom_images').val(JSON.stringify(upload_files));
}

