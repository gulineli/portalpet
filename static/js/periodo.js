function novo_periodo(){
    $('#id_periodos_table').append('<tr><td><div class="input-group date datetime"><input class="form-control periodo_dispache input-sm" type="text"><span class="input-group-addon"><span class="icon-calendar"></span></span></div></td><td><div class="input-group date datetime"><input class="form-control periodo_dispache input-sm" type="text"><span class="input-group-addon"><span class="icon-calendar"></span></span></div></td><td><a id="novo_periodo" class="btn btn-minier" title="clique para excluir este período" rel="tooltip" onclick="exclude_periodo(this);"><i class="icon-trash"></i></a></td></tr>');
}

function exclude_periodo(anchor){
    $this = $(anchor);
    var row = $this.parent().parent();
    var id = row.attr('data-id');
    var url = $('#id-url').val();
    row.remove();
    $.ajax({
          url: url,
          type: "POST",
          datatype: 'json',
          data: {
              id: id,
              ajax: 1,
              remove:true
          },
    });
}

$(function() {
    $('body').on("change",'.datetime',function (e) {
//        var new_date = moment(e.date).format("DD/MM/YYYY h:mm");
        var $row = $(this).parent().parent();
        var id = $row.attr('data-id');
        var url = $('#id-url').val();
        var $periodos = $row.find('.periodo_dispache');
        var $periodo_inicio = $($periodos[0]).val();
        var $periodo_termino = $($periodos[1]).val();
        if ($periodo_inicio && $periodo_termino){
            $.ajax({
                  url: url,
                  type: "POST",
                  data: {
                      id: id,
                      ajax: 1,
                      inicio: $periodo_inicio,
                      termino: $periodo_termino
                  },
                  datatype: 'json',
                  success: function(data) {
                    if (data.success){
                        $row.removeClass('error');
                        if (!id){
                            $row.attr('data-id',data.id);
                        }
                    }
                    else{
                        $row.addClass('error');
                    }
                  }
            });
        }
    });
});
