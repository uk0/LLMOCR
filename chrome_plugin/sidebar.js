function addResult(data) {
    const resultsDiv = document.getElementById('results');
    const resultDiv = document.createElement('div');
    resultDiv.className = 'result';
    resultDiv.innerHTML = `
        <h3>Result ${new Date().toLocaleString()}</h3>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
    resultsDiv.insertBefore(resultDiv, resultsDiv.firstChild);

    // Save to storage
    chrome.storage.local.get({results: []}, function(items) {
        items.results.unshift({
            timestamp: new Date().getTime(),
            data: data
        });
        // Keep only the last 10 results
        if (items.results.length > 10) {
            items.results = items.results.slice(0, 10);
        }
        chrome.storage.local.set({results: items.results});
    });
}

// Load saved results when sidebar is opened
chrome.storage.local.get({results: []}, function(items) {
    items.results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result';
        resultDiv.innerHTML = `
            <h3>Result ${new Date(result.timestamp).toLocaleString()}</h3>
            <pre>${JSON.stringify(result.data, null, 2)}</pre>
        `;
        document.getElementById('results').appendChild(resultDiv);
    });
});

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "showResult") {
        addResult(request.data);
    }
});