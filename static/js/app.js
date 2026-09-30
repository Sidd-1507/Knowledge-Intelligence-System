document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const documentList = document.getElementById('document-list');
    const docCount = document.getElementById('doc-count');
    const vectorCount = document.getElementById('vector-count');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');
    const typingIndicator = document.getElementById('typing-indicator');
    const resetBtn = document.getElementById('reset-btn');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const progressBarContainer = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    // Initial Load
    loadDocuments();
    loadStats();

    // Setup marked options for markdown rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    // Event Listeners
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('show');
    });

    // File Upload Events
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });

    // Chat Events
    sendBtn.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value === '') {
            this.style.height = 'auto';
        }
    });

    resetBtn.addEventListener('click', resetChat);

    // Functions
    async function handleFiles(files) {
        for (let i = 0; i < files.length; i++) {
            await uploadDocument(files[i]);
        }
        fileInput.value = ''; // Reset
    }

    async function uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            progressBarContainer.classList.remove('hidden');
            progressBar.style.width = '0%';
            progressText.innerText = '0%';

            // Simulated progress for visual feedback
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                if (progress > 90) clearInterval(interval);
                progressBar.style.width = `${progress}%`;
                progressText.innerText = `${progress}%`;
            }, 100);

            const response = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData
            });
            
            clearInterval(interval);
            progressBar.style.width = '100%';
            progressText.innerText = '100%';
            
            setTimeout(() => {
                progressBarContainer.classList.add('hidden');
            }, 1000);

            if (response.ok) {
                showToast(`Successfully uploaded ${file.name}`, 'success');
                loadDocuments();
                loadStats();
            } else {
                const data = await response.json();
                showToast(data.error || 'Upload failed', 'error');
            }
        } catch (error) {
            showToast('Error uploading file', 'error');
            progressBarContainer.classList.add('hidden');
        }
    }

    async function loadDocuments() {
        try {
            const response = await fetch('/api/documents/list');
            if (response.ok) {
                const data = await response.json();
                renderDocumentList(data.documents || []);
            }
        } catch (error) {
            console.error('Failed to load documents', error);
        }
    }

    function renderDocumentList(documents) {
        documentList.innerHTML = '';
        if (documents.length === 0) {
            documentList.innerHTML = '<li class="document-item" style="justify-content:center; color: var(--text-secondary);">No documents uploaded</li>';
            return;
        }

        documents.forEach(doc => {
            const li = document.createElement('li');
            li.className = 'document-item';
            
            // Icon based on type
            let icon = 'fa-file';
            if (doc.filename.endsWith('.pdf')) icon = 'fa-file-pdf';
            else if (doc.filename.endsWith('.docx')) icon = 'fa-file-word';
            else if (doc.filename.endsWith('.txt')) icon = 'fa-file-lines';

            li.innerHTML = `
                <div class="doc-info" title="${doc.filename}">
                    <i class="fa-regular ${icon}"></i>
                    <div>
                        <div class="doc-name">${doc.filename}</div>
                        <div class="doc-size">${formatFileSize(doc.size || 0)}</div>
                    </div>
                </div>
                <button class="delete-btn" onclick="deleteDocument('${doc.filename}')" title="Delete">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
            documentList.appendChild(li);
        });
    }

    // Make it available globally for the inline onclick
    window.deleteDocument = async function(filename) {
        if (!confirm(`Are you sure you want to delete ${filename}?`)) return;

        try {
            const response = await fetch(`/api/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showToast(`Deleted ${filename}`, 'success');
                loadDocuments();
                loadStats();
            } else {
                const data = await response.json();
                showToast(data.error || 'Failed to delete', 'error');
            }
        } catch (error) {
            showToast('Error deleting document', 'error');
        }
    };

    async function loadStats() {
        try {
            const response = await fetch('/api/documents/stats');
            if (response.ok) {
                const data = await response.json();
                docCount.innerText = data.sources_count || 0;
                vectorCount.innerText = data.total_chunks || 0;
            }
        } catch (error) {
            console.error('Failed to load stats', error);
        }
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Reset input
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Display user message
        displayMessage(text, 'user');

        // Show loading
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: text })
            });

            hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                displayMessage(data.answer, 'assistant', data.sources);
            } else {
                const data = await response.json();
                displayMessage(data.error || 'Sorry, an error occurred while processing your request.', 'assistant');
                showToast('Error getting response', 'error');
            }
        } catch (error) {
            hideTypingIndicator();
            displayMessage('Network error. Please try again.', 'assistant');
            showToast('Network error', 'error');
        }
    }

    async function resetChat() {
        if (!confirm('Are you sure you want to reset the conversation?')) return;
        
        try {
            const response = await fetch('/api/chat/reset', { method: 'POST' });
            if (response.ok) {
                // Keep only welcome message
                const welcomeMsg = messagesContainer.querySelector('.welcome');
                messagesContainer.innerHTML = '';
                if (welcomeMsg) {
                    messagesContainer.appendChild(welcomeMsg);
                }
                showToast('Conversation reset', 'success');
            }
        } catch (error) {
            showToast('Error resetting chat', 'error');
        }
    }

    function displayMessage(content, type, sources = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;

        const icon = type === 'user' ? 'fa-user' : 'fa-robot';
        
        let contentHtml = content;
        if (type === 'assistant' && typeof marked !== 'undefined') {
            contentHtml = marked.parse(content);
        } else if (type === 'user') {
            // escape html for user input
            contentHtml = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            contentHtml = `<p>${contentHtml}</p>`;
        }

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            const sourceItems = sources.map((s, idx) => `
                <div class="source-item">
                    <div class="source-title">[${idx + 1}] ${s.source || 'Source'}</div>
                    <div class="source-text">${s.content || ''}</div>
                </div>
            `).join('');

            sourcesHtml = `
                <div class="sources-container">
                    <button class="sources-toggle" onclick="this.nextElementSibling.classList.toggle('show')">
                        <i class="fa-solid fa-chevron-down"></i> View Sources (${sources.length})
                    </button>
                    <div class="sources-content">
                        ${sourceItems}
                    </div>
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fa-solid ${icon}"></i>
            </div>
            <div class="message-content">
                ${contentHtml}
                ${sourcesHtml}
            </div>
        `;

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        scrollToBottom();
    }

    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Remove after animation completes
        setTimeout(() => {
            toast.remove();
        }, 3300);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});
