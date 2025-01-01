// background.js
chrome.webNavigation.onCompleted.addListener(function(details) {
  // Inject the content script into the tab when it is fully loaded
  chrome.scripting.executeScript({
    target: { tabId: details.tabId },
    function: injectContentScript
  });
});

function injectContentScript() {
  // Your content script logic goes here
  var url = window.location.href;

  // Simulate server response
  const mockResponse = Math.random() < 0.5 ? 0 : 1; // Replace this with your logic

  if (mockResponse === 1) {
    console.log('Suspicious');
  } else if (mockResponse === 0) {
    console.log('Safe');
  } else {
    console.log('Phishing');
  }
}