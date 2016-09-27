$(document).ready(function() {
	$('#fullpage').fullpage({
		anchors: ['Welcome', 'About', 'Team', 'Portfolio', 'Blog', 'Contact'],
		navigation: true,
		navigationPosition: 'right',
		navigationTooltips: ['Welcome', 'What We Do', 'Our Team', 'Our Work', 'Our Thoughts', 'Get In Touch'],
		responsive:900,
	  	continuousVertical: false,
		scrollOverflow: false
	});
});