document.addEventListener('DOMContentLoaded', function() {
  chrome.runtime.sendMessage({action: "getAnalysisResult"}, function(response) {
    if (response && response.result) {
      document.getElementById('result').textContent = JSON.stringify(response.result, null, 2);
    }
  });
});