/* this function sets the active tab in the nav bar */
function detect(className) {
    var current_url = window.location.href;
    var searchString = '/' + String(current_url).split('/')[3];
    var els = document.querySelectorAll(className);
    for (var i = 0; i < els.length; i++) {
        var url = '/' + String(els[i].href).split('/')[3];
        if (url == searchString) {
            var selected = els[i];
            break;
        }
    }
    return selected
}

try {
    var detected = detect('.nav-link');
    if (detected != undefined) {
        detected.parentElement.className += ' active';
    }
}
catch(e) {
    console.log(e);
}
