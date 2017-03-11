function preloader() {
            var loadMessage = document.getElementById("loading");
            loadMessage.innerHTML = "Please let us check in with Google <br> <br> (this may take a bit depending on traffic)";
        };


function signInCallback(authResult) {
  if (authResult['code']) {
    // Hide the sign-in button now that the user is authorized
    $('#signInButton').attr('style', 'display: none');
    //display loading message while we wait for auth
    preloader()
    // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
    $.ajax({
      type: 'POST',
      url: '/gconnect?state='.concat(state),
      processData: false,
      data: authResult['code'],
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
        // Handle or verify the server response if necessary.
        if (result) {
            console.log('gauth worked!!')
            $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
         setTimeout(function() {
             window.location.href = "/";
         }, 4000);

      } else if (authResult['error']) {
    console.log('There was an error with gauth: ' + authResult['error']);
  } else {
        $('#result').html('Failed to make a server-side call. Check your configuration and console.');
         }
      }}); } }
