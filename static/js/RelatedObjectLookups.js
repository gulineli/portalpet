function html_unescape(text){
    text=text.replace(/&lt;/g,'<');
    text=text.replace(/&gt;/g,'>');
    text=text.replace(/&quot;/g,'"');
    text=text.replace(/&#39;/g,"'");
    text=text.replace(/&amp;/g,'&');
    return text;
}

function id_to_windowname(text){
    text=text.replace(/\./g,'__dot__');
    text=text.replace(/\-/g,'__dash__');
    return text;
}

function windowname_to_id(text){
    text=text.replace(/__dot__/g,'.');
    text=text.replace(/__dash__/g,'-');
    return text;
}

function showAddAnotherPopup(triggeringLink){
    var name=triggeringLink.id.replace(/^add_/,'');
    name=id_to_windowname(name);
    href=triggeringLink.href
    if(href.indexOf('?_popup=')==-1){
        if(href.indexOf('?')==-1){
            href+='?_popup=';
            triggeringLink.href=href+name
        }
        else{
            href+='&_popup=';
            triggeringLink.href=href+name
        }
    }
    return false;
}

function linkid(triggeringLink){
    var name=triggeringLink.id.replace(/^add_/,'');
    var inicio=triggeringLink.href.lastIndexOf("_");
    var texto=triggeringLink.href
    var id_ext=texto.substring(inicio+1,texto.length);
    inicio=triggeringLink.href.lastIndexOf("i");
    var href=texto.substring(0,inicio);
    var select=document.getElementById("id_funcao");
    href+=select.value;
    href+="/"
    href+=id_ext;
    window.location.href=href;
    return false;
}

function dismissAddAnotherPopup(newId,newRepr,id_field){
    $.fn.colorbox.close();
    if (newId){
        var opt = $("#"+id_field + " [value=" + newId +"]");
        if (opt.length){
            opt.attr("selected","selected");
            opt.html(newRepr);
            $("#"+id_field).focus();
        }else{
            $("#"+id_field).append('<option value="'+newId+'"selected="selected">'+ newRepr +'</option>').focus();
        }

    }
}
