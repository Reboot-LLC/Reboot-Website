(function() {
    'use strict';
    var $btnVC = $(".btnVC"),
        $closeVC = $(".closeVC"),
        $wrapVC = $(".wrapVC"),
        $rippleVC = $(".rippleVC"),
        $layeredVC = $(".layeredVC");

    $btnVC.on("click", function() {
        $rippleVC.addClass("rippling");
        $wrapVC.addClass("clicked");
        setTimeout(function() {
            $layeredVC.addClass("active");
        }, 1500);
    });

    $closeVC.on("click", function() {
        $wrapVC.removeClass("clicked");
        $rippleVC.removeClass("rippling");
        $layeredVC.removeClass("active");
    });

})();

(function() {
    'use strict';
    var $btnST = $(".btnST"),
        $closeST = $(".closeST"),
        $wrapST = $(".wrapST"),
        $rippleST = $(".rippleST"),
        $layeredST = $(".layeredST");

    $btnST.on("click", function() {
        $rippleST.addClass("rippling");
        $wrapST.addClass("clicked");
        setTimeout(function() {
            $layeredST.addClass("active");
        }, 1500);
    });

    $closeST.on("click", function() {
        $wrapST.removeClass("clicked");
        $rippleST.removeClass("rippling");
        $layeredST.removeClass("active");
    });
    
})();

(function() {
    'use strict';
    var $btnTS = $(".btnTS"),
        $closeTS = $(".closeTS"),
        $wrapTS = $(".wrapTS"),
        $rippleTS = $(".rippleTS"),
        $layeredTS = $(".layeredTS");

    $btnTS.on("click", function() {
        $rippleTS.addClass("rippling");
        $wrapTS.addClass("clicked");
        setTimeout(function() {
            $layeredTS.addClass("active");
        }, 1500);
    });

    $closeTS.on("click", function() {
        $wrapTS.removeClass("clicked");
        $rippleTS.removeClass("rippling");
        $layeredTS.removeClass("active");
    });
    
})();

(function() {
    'use strict';
    var $btnMT = $(".btnMT"),
        $closeMT = $(".closeMT"),
        $wrapMT = $(".wrapMT"),
        $rippleMT = $(".rippleMT"),
        $layeredMT = $(".layeredMT");

    $btnMT.on("click", function() {
        $rippleMT.addClass("rippling");
        $wrapMT.addClass("clicked");
        setTimeout(function() {
            $layeredMT.addClass("active");
        }, 1500);
    });

    $closeMT.on("click", function() {
        $wrapMT.removeClass("clicked");
        $rippleMT.removeClass("rippling");
        $layeredMT.removeClass("active");
    });
    
})();