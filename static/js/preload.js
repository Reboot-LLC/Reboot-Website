jQuery(document).ready(function(){
	delayShow();
});
 
function delayShow() {
	var secs = 500; 
	var secs2 = 600;
	setTimeout('jQuery(".loading-gif").css("visibility","hidden");', secs);
	setTimeout('jQuery("body").css("visibility","visible");', secs2);
}