var device = $('.devices a');
device.on('click', function(e) {
  e.preventDefault();
  var type = $(this).attr('class');
  console.log(type);
  $('.browser').attr('class', 'browser ' + type);
});