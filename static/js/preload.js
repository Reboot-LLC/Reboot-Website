jQuery(document).ready(function(){
	delayShow();
});
 
function delayShow() {
	var secs = 3000;
	var secs2 = 3300;
	setTimeout('jQuery(".loading-gif").css("visibility","hidden");', secs);
	setTimeout('jQuery("body").css("visibility","visible");', secs2);
}