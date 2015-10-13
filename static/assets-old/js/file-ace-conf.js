
jQuery(function($) {
    $.each($('.file-ace'),function (index,c){
        var component = $(c);
        var is_image= component.attr('data-image') | false
        
        component.ace_file_input({
		    no_file:'Nenhum ...',
		    btn_choose:'Escolha',
		    btn_change:'Alterar',
		    droppable:false,
		    onchange:null,
		    thumbnail:false, //| true | large
		    //whitelist:'gif|png|jpg|jpeg'
		    blacklist:'exe|php'
	    });
	    component.ace_file_input('enable');
    });
});
