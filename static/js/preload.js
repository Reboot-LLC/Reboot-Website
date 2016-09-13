jQuery(document).ready(function(){
	delayShow();
});
 
function delayShow() {
	var secs = 1000;
	var secs2 = 1100;
	setTimeout('jQuery(".loading-gif").css("visibility","hidden");', secs);
	setTimeout('jQuery("body").css("visibility","visible");', secs2);
}