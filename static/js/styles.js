/* check if the project is using jQuery and set the appropriate value */
if (window.jQuery) { var V = $.Velocity; } else {var V = Velocity; }


/* grabbing the window attributes for certain things */
var w = window,
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    x = w.innerWidth || e.clientWidth || g.clientWidth,
    y = w.innerHeight|| e.clientHeight|| g.clientHeight;


/* http://stackoverflow.com/a/27067033/5441252 */
/* modified to include random timeout for more human-like typing */
function printLetterByLetter(destination, message, speed, randomFlag) {
    var random;
    var i = 0;
    if (randomFlag == true) {
        random = Math.floor(Math.random() * 2000)
    }
    else {
        random = 0;
    }
    var interval = setInterval(function () {
        setTimeout(function () {
            document.getElementById(destination).innerHTML += message.charAt(i);
            i++;
            if (i > message.length) {
                clearInterval(interval);
            }
        }, random);
    }, speed)
}


/* http://stackoverflow.com/a/987376/5441252 */
/* used to select text inside a div */
function SelectText(element) {
    var doc = document,
        text = doc.getElementById(element),
        range,
        selection;
    if (doc.body.createTextRange) {
        range = document.body.createTextRange();
        range.moveToElementText(text);
        range.select();
    } else if (window.getSelection) {
        selection = window.getSelection();
        range = document.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
    }
}


/* https://gist.github.com/lrvick/2080648 */
RGBToHex = function (r, g, b) {
    var bin = r << 16 | g << 8 | b;
    return (function (h) {
        return new Array(7 - h.length).join("0") + h
    })(bin.toString(16).toUpperCase())
};


/* modal close */
function modalClose() {
    var modal = document.getElementById('modal-success');
    V(modal, {opacity: 0}, {duration: 500});
}
