window.globals.append_resource_link_id = function(url){
    if (!url.match(/resource_link_id/)) {
        if (!url.match(/\?/g)) {
            url += '?';
        }
        return url + '&resource_link_id=' + window.globals.RESOURCE_LINK_ID;
    }
};

$(document).ajaxSend(function(event, jqxhr, settings){
    settings.url = window.globals.append_resource_link_id(settings.url);
});
