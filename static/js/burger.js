$('.menu-btn').click(function(e) {
	e.preventDefault();
	if ($(this).hasClass('active')) {
		$('body').removeClass('scroll-hidden');
		$(this).removeClass('active');
		$('.mobile-menu').removeClass('open');
		$('.overlay').fadeOut();
	}
	else
	{
		$('.menu-btn').removeClass('active');
		$('.mobile-menu').removeClass('open');
		$('body').removeClass('scroll-hidden');
		$('.modal').removeClass('open')
		$(this).addClass('active');
		$('.mobile-menu').addClass('open');
		$('body').addClass('scroll-hidden');
		$('.overlay').fadeIn();
	}
});

$('.overlay').click(function() {
	$('.mobile-menu').removeClass('open');
	$('.menu-btn').removeClass('active');
	$('.modal').removeClass('open');
	$('body').removeClass('scroll-hidden');
	$(this).fadeOut();
});

$('.mobile-link').click(function() {
	$('.mobile-menu').removeClass('open');
	$('.menu-btn').removeClass('active');
	$('body').removeClass('scroll-hidden');
	$('.overlay').fadeOut();
});

$('.login-btn', ).click(function() {
	$('#loginModal').addClass('open');
	$('body').addClass('scroll-hidden');
	$('.overlay').fadeIn();
});

$('.registr-btn', ).click(function() {
	$('#registerModal').addClass('open');
	$('body').addClass('scroll-hidden');
	$('.overlay').fadeIn();
});

$('.mobile-registr-btn', ).click(function() {
	if ($('#registerModal').hasClass('open')) {
		$('#registerModal').removeClass('open')
		$('.overlay').fadeOut();
		$('body').removeClass('scroll-hidden');
	}
	else {
		$('#registerModal').addClass('open');
		$('.mobile-menu').removeClass('open');
		$('.menu-btn').removeClass('active');
		$('body').addClass('scroll-hidden');
		$('.overlay').fadeIn();
	}
});

$('.mobile-login-btn', ).click(function() {
	if ($('#loginModal').hasClass('open')) {
		$('#loginModal').removeClass('open')
		$('.overlay').fadeOut();
		$('body').removeClass('scroll-hidden');
	}
	else {
		$('#loginModal').addClass('open');
		$('.mobile-menu').removeClass('open');
		$('.menu-btn').removeClass('active');
		$('body').addClass('scroll-hidden');
		$('.overlay').fadeIn();
	}
});

$('.modal-close').click(function() {
	$('.modal.open').removeClass('open')
	$('.overlay').fadeOut();
	$('body').removeClass('scroll-hidden');
});