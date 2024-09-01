let sidebar = null;
let toggleButton = null;

function createSidebar() {
    if (sidebar) return;

    // Create toggle button
    toggleButton = document.createElement('div');
    toggleButton.id = 'image-analyzer-toggle';
    toggleButton.textContent = 'Image Analysis';
    toggleButton.addEventListener('click', toggleSidebar);
    document.body.appendChild(toggleButton);

    // Create sidebar
    sidebar = document.createElement('div');
    sidebar.id = 'image-analyzer-sidebar';

    // Create close button
    const closeButton = document.createElement('span');
    closeButton.id = 'image-analyzer-close';
    closeButton.textContent = '×';
    closeButton.addEventListener('click', closeSidebar);
    sidebar.appendChild(closeButton);

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = chrome.runtime.getURL('sidebar.html');
    iframe.style.width = '100%';
    iframe.style.height = 'calc(100% - 40px)';
    iframe.style.border = 'none';
    sidebar.appendChild(iframe);

    document.body.appendChild(sidebar);
}

function toggleSidebar() {
    if (sidebar.classList.contains('open')) {
        closeSidebar();
    } else {
        openSidebar();
    }
}

function openSidebar() {
    sidebar.classList.add('open');
    toggleButton.style.display = 'none';
}

function closeSidebar() {
    sidebar.classList.remove('open');
    toggleButton.style.display = 'block';
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "showResult") {
        createSidebar();
        openSidebar();
        sidebar.querySelector('iframe').contentWindow.postMessage({action: "showResult", data: message.data}, "*");
    } else if (message.action === "showError") {
        alert(`Error: ${message.error}`);
    }
});