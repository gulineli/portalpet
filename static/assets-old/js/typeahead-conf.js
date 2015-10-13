
jQuery(function($) {
    $(document.body).on('click','.resume a',function(event){
        event.preventDefault();
        var element = $(this);
        var id = element.attr('id');
        var hidden = element.parent().prev().find('input[type=hidden]');
        hidden.val('');   // hidden.val().replace('|'+id+'|','|') );
        $(this).remove();
    });
    
    $.each($('.bt_autocomplete'),function(index,value){
        var component = $(value);
        var url = component.attr('data-url');
        var show_result = component.attr('data-resume');
        component.typeahead({
              matcher: function (item) {
                return true
              }
            , highlighter: function (item) {
                if (item.value){
                  var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&')
                  return item.value.replace(new RegExp('(' + query + ')', 'ig'), function ($1, match) {
                    return '<strong>' + match + '</strong>'
                  }) || item.value
                }
              }
            , source: function(query, process) {
                $.ajax({
                    url: url ,
                    dataType: "json",
                    type: "POST",
                    data: {
                        max_rows: 15,
                        search_key: query,
                        ajax: 1
                    },
                    success: function(data) {
                      var return_list = [], i = data.length;
                      while (i--) {
                          if (data[i].title){
                            if(data[i]._class){
                              return_list[i] = {id: data[i].id, value: data[i].value,_class: data[i]._class,title: data[i].title};
                            }
                            else{
                              return_list[i] = {id: data[i].id, value: data[i].value,title: data[i].title};
                            }
                          }
                          else if(data[i]._class){
                            return_list[i] = {id: data[i].id, value: data[i].value,_class: data[i]._class};
                          }
                          else{
                            return_list[i] = {id: data[i].id, value: data[i].value};
                          }
                      }
                      process(return_list);
                    }
                });
            },
            updater: function(obj) {
                component.val(obj.value);
                component.prev('input[type=hidden]').val(obj.id).trigger('change');
                if (show_result){
                  component.val('');
                  component.parent().parent().find('.resume').html('<a id="' + obj.id + '_trash" class="btn btn-sm" > \
                        <i class="icon-trash"></i> ' + obj.value + '</a>');
                }
            }
          });
      });

});
