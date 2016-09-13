$(document).ready(function() {
	$('#fullpage').fullpage({
		anchors: ['Welcome', 'About', 'Team', 'Blog', 'Contact'],
		navigation: true,
		navigationPosition: 'right',
		navigationTooltips: ['Welcome', 'What We Do', 'Our Team', 'Our Thoughts', 'Get In Touch'],
		responsive:900,
	  	continuousVertical: false,
		scrollOverflow: false
	});



	$('.fancybox').fancybox();
	$('.fancybox-thumbs').fancybox({
		prevEffect : 'none',
		nextEffect : 'none',

		closeBtn  : false,
		arrows    : false,
		nextClick : true,

		helpers : {
			thumbs : {
				width  : 50,
				height : 50
			}
		}
	});

	  $("#owl-demo").owlCarousel({
 
      autoPlay: 3000, //Set AutoPlay to 3 seconds
 
      items : 3,
      itemsDesktop : [1199,3],
      itemsDesktopSmall : [979,3],
      pagination: false,
      navigation: false,
      paginationSpeed: 200,
      rewindSpeed: 300
 
  });

});


// Wow js activation
 new WOW().init();