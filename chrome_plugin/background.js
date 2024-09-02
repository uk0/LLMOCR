chrome.contextMenus.create(
    {
      id: "analyzeImageYYY",
      title: "Analyze Image",
      contexts: ["image"]
    }
);

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyzeImageYYY") {
    analyzeImage(info.srcUrl, tab.id);
  }
});

function analyzeImage(imageUrl, tabId) {
  console.log('Fetching image from:', imageUrl);
  fetch(imageUrl, { mode: 'no-cors' })
    .then(res => {
      if (!res.ok && res.type !== 'opaque') {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.blob();
    })
    .then(blob => {
      console.log('Image fetched successfully, size:', blob.size);
      const formData = new FormData();
      formData.append('image', blob, 'image.jpg');

      console.log('Sending analysis request to http://localhost:8510/analyze');
      return fetch('http://localhost:8510/analyze', {
        method: 'POST',
        body: formData
      });
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Analysis server HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Analysis Result:', data);
      showResult(tabId, data);
    })
    .catch(error => {
      console.error('Error:', error);
      showError(tabId, error.toString());
    });
}

function showResult(tabId, data) {
    chrome.tabs.sendMessage(tabId, {action: "showResult", data: data});
}

function showError(tabId, errorMessage) {
  chrome.tabs.sendMessage(tabId, {action: "showError", error: errorMessage}, function(response) {
    if (chrome.runtime.lastError) {
      console.error('Error sending message to tab:', chrome.runtime.lastError);
      alert(`Error: ${errorMessage}`);
    }
  });
}