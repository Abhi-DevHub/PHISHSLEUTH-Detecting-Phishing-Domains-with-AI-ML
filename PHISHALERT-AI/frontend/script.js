// script.js
// After a delay, hide the overlay and show the main content
setTimeout(function () {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('main-content').style.display = 'block';
  }, 5000); // Adjust the delay (in milliseconds) as needed