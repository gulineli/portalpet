$.editable.addInputType('redactor', {
    element : function(settings, original) {
        var textarea = $('<textarea />');
        if (settings.rows) {
            textarea.attr('rows', settings.rows);
        } else {
            textarea.height(settings.height);
        }
        if (settings.cols) {
            textarea.attr('cols', settings.cols);
        } else {
            textarea.width(settings.width);
        }
        textarea.attr('id','value_' + original.id);
        $(this).append(textarea);
        return(textarea);

    },
    plugin : function(settings, original) {
        $('textarea', this).redactor({ lang: 'pt_br' });
    }
});
