jQuery(document).ready(function(){
	delayShow();
});
 
function delayShow() {
	var secs = 2000; 
	var secs2 = 2100;
	setTimeout('jQuery(".loading-gif").css("visibility","hidden");', secs);
	setTimeout('jQuery("body").css("visibility","visible");', secs2);
}