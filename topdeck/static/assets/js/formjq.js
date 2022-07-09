$('#password, #confirm_password').on('keyup', function () {
    if ($('#password').val() == $('#confirm_password').val()) {
      $('#message').html('Matching').css('color', 'green');
    } else 
      $('#message').html('Not Matching').css('color', 'red');
  })(jQuery); 

$('.validatedForm').validate({
    rules: {
      password: {
        minlength: 4
      },
      password_confirm: {
        minlength: 4,
        equalTo: "#password"
      }
    }
  });
  
  $('button').click(function() {
    console.log($('.validatedForm').valid());
  })(jQuery);