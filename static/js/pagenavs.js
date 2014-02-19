function setUrlVars(v) {
    v = v ? v : {};
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
      vars[key] = value;
      return '';
    });

    for(var key in v){
      vars[key] = v[key];
    }
    first=true;
    for(var key in vars){
      if (first){
        first=false;
        parts=parts+'?'+key+'='+vars[key];
      } else{
        parts=parts+'&'+key+'='+vars[key];
      }
    }
    return parts;
  }
