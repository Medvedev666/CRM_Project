$('.login-btn').click(function(o) {
  if ($(this).hasClass('open')) {
  $(this).removeClass('open');
  $('.overlay').fadeOut();
  }
  else
  {
  $(this).removeClass('open');
  $(this).addClass('open');
  $('body').addClass('scroll-hidden');
  $('.overlay').fadeIn();
	}
});

document.getElementById("")

$('.overlay').click(function() {
	$('.login-btn').removeClass('open');
	$('body').removeClass('scroll-hidden');
	$(this).fadeOut();
});