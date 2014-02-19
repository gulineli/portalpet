$.editable.addInputType('multiselect', {
    element : function(settings, original) {
                    var select = $('<select multiple="multiple"/>');
                    $(this).append(select);
                    return(select);
                },
    content : function(data, settings, original) {
        /* If it is string assume it is json. */
        if (String == data.constructor) {      
            eval ('var json = ' + data);
        } else {
        /* Otherwise assume it is a hash already. */
            var json = data;
        }
        for (var key in json) {
            if (!json.hasOwnProperty(key)) {
                continue;
            }
            if ('selected' == key) {
                continue;
            } 
            var option = $('<option />').val(key).append(json[key]);
            $('select', this).append(option);    
        }                    
        /* Loop option again to set selected. IE needed this... */ 
        $('select', this).children().each(function() {
            if ($(this).val() == json['selected'] || 
                $(this).text() == $.trim(original.revert)) {
                    $(this).attr('selected', 'selected');
            }
        });
        /* Submit on change if no submit button defined. */
        if (!settings.submit) {
            var form = this;
            $('select', this).change(function() {
                form.submit();
            });
        }
    }
});
