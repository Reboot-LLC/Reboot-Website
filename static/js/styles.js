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


/* github feed */
var feedIndex = 0;
function displayGit(source) {
    // get the length of the json object
    var max_index = Object.keys(source).length;

    // delete the current element from the dom
    var element = document.getElementById('css-typing');
    element.parentElement.removeChild(element);

    // create a new element
    var newElement = document.createElement('a');
    newElement.id = 'css-typing';
    newElement.class = 'css-typing';
    document.getElementById('css-typing-container').appendChild(newElement);

    // set the content
    printLetterByLetter('css-typing', String(source[feedIndex]['name'] + ': ' + source[feedIndex]['description']), 50, true);
    document.getElementById('css-typing').href = String(source[feedIndex]['url']);
    document.getElementById('css-typing').setAttribute('target', '_blank');

    // set index
    if (feedIndex < max_index - 1) {
        feedIndex += 1;
    }
    else {
        feedIndex = 0;
    }
}

setInterval(function () {
    displayGit(github)
}, 10000);


/* YO MIKEY HERE IS SOME EXAMPLE CODE THAT USES VELOCITY.JS FROM MY WEB SITE */

///* click actions */
//function slideMenu() {
//    // set some parameters
//    var menu = document.getElementById("menu-container");
//    var menuIcon = document.getElementById("menu-icon");
//    if (x * 0.17 < 280) {
//        var translation = 280
//    }
//    else {
//        translation = -x + (x * 0.17);
//    }
//
//    // if the menu is open
//    if (menu.className.match(/\bmenu-container-show\b/)) {
//        document.getElementById("menu-container").className =
//            document.getElementById("menu-container").className.replace(/(?:^|\s)menu-container-show(?!\S)/g, '');
//        Velocity(menuIcon, {rotateZ: "0deg", translateX: 0 + "px"}, {duration: 0});
//    }
//    // else menu is closed
//    else {
//        menu.className += " menu-container-show";
//        Velocity(menuIcon, {translateX: translation + "px", rotateZ: "180deg"}, {duration: 500});
//    }
//}
//
//
///* animations */
//// set the initial view
//var currentView;
//currentView = 'welcome';
//
//// hide elements initially
//Velocity(document.getElementById('about'), {opacity: 0});
//Velocity(document.getElementById('portfolio'), {opacity: 0});
//Velocity(document.getElementById('resume'), {opacity: 0});
//Velocity(document.getElementById('hire'), {opacity: 0});
//
//function menuClick(target, menuId) {
//    // get the translation amount
//    if (y >= 964) {
//        var translationShow = -(y * 0.25) + "px";
//        var translationHide = (y * 0.25) + "px";
//    }
//    else {
//        translationShow = -(y * 0.55) + "px";
//        translationHide = (y * 0.55) + "px";
//    }
//
//    // hide the current view and push down
//    Velocity(document.getElementById(currentView), {opacity: 0, translateY: translationHide}, {duration: 1500});
//    document.getElementById(target).style.zIndex = 499;
//
//    // change the current view
//    currentView = target;
//
//    // show the selected view and push up
//    Velocity(document.getElementById(target), {opacity: 1, translateY: translationShow}, {duration: 1500});
//    document.getElementById(target).style.zIndex = 500;
//
//    /
//    // reset any elements that were previously selected
//    if (x > 1124) {
//        Velocity(document.getElementsByClassName('portfolio-text'), {opacity: 0}, {duration: 750});
//        Velocity(document.getElementsByClassName('portfolio-label-bgd-small'), {width: "170px"}, {duration: 750});
//        Velocity(document.getElementsByClassName('portfolio-label-bgd'), {width: "270px"}, {duration: 750});
//    }
//
//    // set the width of the selected element
//    if (self.style.width != "100%") {
//        Velocity(self, {width: "100%"}, {duration: 750});
//        Velocity(portfolioText, {opacity: 1}, {duration: 1250});
//    }
//}/ get the background color to apply
//    var selectedMenuButton = document.getElementById(menuId),
//        styles = window.getComputedStyle(selectedMenuButton),
//        bc = styles.getPropertyValue('background-color');
//
//    // get the r, g, b values for hex conversion (velocity only accepts hex strings)
//    var rgb = bc.match(/\(([^)]+)\)/)[1];
//    var r = rgb.split(",")[0];
//    var g = rgb.split(",")[1];
//    var b = rgb.split(",")[2];
//
//    // convert the rgb to hex
//    var hex = "#" + RGBToHex(r, g, b);
//
//    // apply a background color to the selected menu item and change the rest back to default
//    Velocity(document.getElementsByClassName('menu-key'), {backgroundColor: "#666"}, {duration: 750});
//    Velocity(document.getElementById(menuId), {backgroundColor: hex}, {duration: 750});
//}
//
//function portfolioClick(self) {
//    // get any elements we need to animate
//    var portfolioText = self.getElementsByClassName('portfolio-text')[0];
