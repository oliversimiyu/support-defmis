/**
 * DEFMIS Chat Widget - Embeddable Customer Support Chat
 * 
 * Usage:
 * <script>
 *   window.DEFMISChat = {
 *     apiUrl: 'http://localhost:8000',
 *     customerId: null, // Auto-generated if not provided
 *     customerName: '', // Optional
 *     customerEmail: '' // Optional
 *   };
 * </script>
 * <script src="http://localhost:8000/static/js/chat-widget.js"></script>
 */

(function() {
    'use strict';

    // Configuration
    const config = {
        apiUrl: window.DEFMISChat?.apiUrl || 'http://localhost:8000',
        customerId: window.DEFMISChat?.customerId || localStorage.getItem('defmis_customer_id') || null,
        customerName: window.DEFMISChat?.customerName || localStorage.getItem('defmis_customer_name') || '',
        customerEmail: window.DEFMISChat?.customerEmail || localStorage.getItem('defmis_customer_email') || ''
    };

    let chatSession = null;
    let socket = null;
    let widgetConfig = null;
    let isConnected = false;
    let unreadCount = 0;
    let isWidgetOpen = false;
    let lastNotificationTime = 0;

    // Generate unique customer ID if not provided
    if (!config.customerId) {
        config.customerId = 'customer_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('defmis_customer_id', config.customerId);
    }

    // Widget HTML structure
    const createWidgetHTML = () => {
        const position = widgetConfig?.widget_position || 'bottom-right';
        const primaryColor = widgetConfig?.primary_color || '#007bff';
        
        return `
            <div id="defmis-chat-widget" style="
                position: fixed;
                ${position === 'bottom-right' ? 'bottom: 20px; right: 20px;' : 'bottom: 20px; left: 20px;'}
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <!-- Chat Toggle Button -->
                <div id="defmis-chat-toggle" style="
                    width: 60px;
                    height: 60px;
                    background-color: ${primaryColor};
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                    position: relative;
                ">
                    <svg id="defmis-chat-icon" width="24" height="24" fill="white" viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                    </svg>
                    <svg id="defmis-close-icon" width="24" height="24" fill="white" viewBox="0 0 24 24" style="display: none;">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                    
                    <!-- Notification Badge -->
                    <div id="defmis-notification-badge" style="
                        position: absolute;
                        top: -5px;
                        right: -5px;
                        background-color: #dc3545;
                        color: white;
                        border-radius: 50%;
                        width: 20px;
                        height: 20px;
                        font-size: 11px;
                        font-weight: bold;
                        display: none;
                        align-items: center;
                        justify-content: center;
                        animation: pulse 2s infinite;
                    ">
                        0
                    </div>
                </div>

                <!-- Chat Window -->
                <div id="defmis-chat-window" style="
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                    display: none;
                    flex-direction: column;
                    position: absolute;
                    ${position === 'bottom-right' ? 'bottom: 80px; right: 0;' : 'bottom: 80px; left: 0;'}
                ">
                    <!-- Header -->
                    <div style="
                        background-color: ${primaryColor};
                        color: white;
                        padding: 15px;
                        border-radius: 10px 10px 0 0;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    ">
                        <img src="${config.apiUrl}/static/images/logo.png" alt="Logo" style="
                            width: 32px;
                            height: 32px;
                            object-fit: contain;
                            background: white;
                            border-radius: 6px;
                            padding: 4px;
                        ">
                        <div style="flex: 1;">
                            <div>${widgetConfig?.name || 'Customer Support'}</div>
                            <div id="defmis-connection-status" style="font-size: 12px; margin-top: 2px; opacity: 0.8;">
                                Connecting...
                            </div>
                        </div>
                    </div>

                    <!-- Messages Area -->
                    <div id="defmis-messages" style="
                        flex: 1;
                        padding: 15px;
                        overflow-y: auto;
                        background-color: #f8f9fa;
                    ">
                        <div class="defmis-message defmis-message-admin" style="
                            background: white;
                            padding: 10px 12px;
                            border-radius: 18px;
                            margin-bottom: 10px;
                            max-width: 80%;
                            font-size: 14px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                            ${widgetConfig?.welcome_message || 'Hi there! How can we help you today?'}
                        </div>
                    </div>

                    <!-- Customer Info Form -->
                    <div id="defmis-customer-form" style="
                        padding: 20px;
                        border-top: 1px solid #eee;
                        background: white;
                        border-radius: 0 0 10px 10px;
                    ">
                        <div style="margin-bottom: 15px; text-align: center;">
                            <h4 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">Start a Conversation</h4>
                            <p style="margin: 0; color: #666; font-size: 14px;">Please provide your details to get started</p>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; color: #333; font-size: 14px; font-weight: 500;">Name *</label>
                            <input 
                                type="text" 
                                id="defmis-customer-name" 
                                placeholder="Enter your name"
                                required
                                style="
                                    width: 100%;
                                    padding: 10px 12px;
                                    border: 1px solid #ddd;
                                    border-radius: 6px;
                                    outline: none;
                                    font-size: 14px;
                                    box-sizing: border-box;
                                "
                            />
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 5px; color: #333; font-size: 14px; font-weight: 500;">Email *</label>
                            <input 
                                type="email" 
                                id="defmis-customer-email" 
                                placeholder="Enter your email"
                                required
                                style="
                                    width: 100%;
                                    padding: 10px 12px;
                                    border: 1px solid #ddd;
                                    border-radius: 6px;
                                    outline: none;
                                    font-size: 14px;
                                    box-sizing: border-box;
                                "
                            />
                        </div>
                        
                        <button 
                            id="defmis-start-chat-button"
                            style="
                                width: 100%;
                                background-color: ${primaryColor};
                                color: white;
                                border: none;
                                padding: 12px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 14px;
                                font-weight: 500;
                                transition: background-color 0.3s;
                            "
                        >
                            Start Chat
                        </button>
                    </div>

                    <!-- Input Area (hidden initially) -->
                    <div id="defmis-chat-input" style="
                        padding: 15px;
                        border-top: 1px solid #eee;
                        background: white;
                        border-radius: 0 0 10px 10px;
                        display: none;
                    ">
                        <div style="display: flex; gap: 10px; margin-bottom: 10px; align-items: center;">
                            <button 
                                id="defmis-attachment-button"
                                title="Attach file"
                                style="
                                    background: none;
                                    border: 1px solid #ddd;
                                    padding: 8px;
                                    border-radius: 50%;
                                    cursor: pointer;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    transition: background-color 0.3s;
                                "
                                onmouseover="this.style.backgroundColor='#f0f0f0';"
                                onmouseout="this.style.backgroundColor='transparent';"
                            >
                                <svg width="20" height="20" fill="#666" viewBox="0 0 24 24">
                                    <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
                                </svg>
                            </button>
                            <input 
                                type="file" 
                                id="defmis-file-input" 
                                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt"
                                style="display: none;"
                            />
                            <input 
                                type="text" 
                                id="defmis-message-input" 
                                placeholder="Type your message..."
                                style="
                                    flex: 1;
                                    padding: 10px 12px;
                                    border: 1px solid #ddd;
                                    border-radius: 20px;
                                    outline: none;
                                    font-size: 14px;
                                "
                            />
                            <button 
                                id="defmis-send-button"
                                style="
                                    background-color: ${primaryColor};
                                    color: white;
                                    border: none;
                                    padding: 10px 15px;
                                    border-radius: 50%;
                                    cursor: pointer;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                "
                            >
                                <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                        </div>
                        <div id="defmis-file-preview" style="display: none; padding: 8px; background: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span id="defmis-file-name" style="font-size: 12px; color: #666;"></span>
                                <button id="defmis-remove-file" style="background: none; border: none; color: #dc3545; cursor: pointer; font-size: 18px;">×</button>
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <button 
                                id="defmis-close-conversation-button"
                                style="
                                    background: none;
                                    border: 1px solid #dc3545;
                                    color: #dc3545;
                                    padding: 6px 12px;
                                    border-radius: 4px;
                                    cursor: pointer;
                                    font-size: 12px;
                                    transition: all 0.3s;
                                "
                                onmouseover="this.style.backgroundColor='#dc3545'; this.style.color='white';"
                                onmouseout="this.style.backgroundColor='transparent'; this.style.color='#dc3545';"
                            >
                                End Conversation
                            </button>
                        </div>
                    </div>
                    
                    <!-- Conversation Closed Message -->
                    <div id="defmis-conversation-closed" style="
                        padding: 20px;
                        border-top: 1px solid #eee;
                        background: #f8f9fa;
                        border-radius: 0 0 10px 10px;
                        text-align: center;
                        display: none;
                    ">
                        <div style="color: #6c757d; font-size: 14px; margin-bottom: 10px;">
                            <i class="fas fa-check-circle" style="margin-right: 5px; color: #28a745;"></i>
                            <span id="defmis-closed-message">This conversation has been closed.</span>
                        </div>
                        <button 
                            id="defmis-new-conversation-button"
                            style="
                                background-color: ${primaryColor};
                                color: white;
                                border: none;
                                padding: 8px 16px;
                                border-radius: 4px;
                                cursor: pointer;
                                font-size: 12px;
                            "
                        >
                            Start New Conversation
                        </button>
                    </div>
                </div>
            </div>
        `;
    };

    // Initialize widget
    const initWidget = async () => {
        try {
            // Get widget configuration
            const configResponse = await fetch(`${config.apiUrl}/chat/api/widget/config/`);
            widgetConfig = await configResponse.json();

            // Create widget HTML
            document.body.insertAdjacentHTML('beforeend', createWidgetHTML());

            // Set up event listeners
            setupEventListeners();

            // Check if customer info exists
            if (config.customerName && config.customerEmail) {
                // Initialize chat session with existing info
                await initChatSession();
                showChatInterface();
                // Initialize WebSocket
                initWebSocket();
            } else {
                // Show customer info form
                showCustomerForm();
            }

            // Request notification permission
            if ('Notification' in window && Notification.permission === 'default') {
                Notification.requestPermission();
            }

            console.log('DEFMIS Chat Widget initialized successfully');
        } catch (error) {
            console.error('Error initializing chat widget:', error);
        }
    };

    // Initialize chat session
    const initChatSession = async () => {
        try {
            const response = await fetch(`${config.apiUrl}/chat/api/chat/start/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_id: config.customerId,
                    customer_name: config.customerName,
                    customer_email: config.customerEmail
                })
            });

            const data = await response.json();
            chatSession = data.chat_session;

            // Load chat history
            await loadChatHistory();
        } catch (error) {
            console.error('Error initializing chat session:', error);
        }
    };

    // Load chat history
    const loadChatHistory = async () => {
        try {
            const response = await fetch(`${config.apiUrl}/chat/api/chat/${config.customerId}/history/`);
            const messages = await response.json();

            const messagesContainer = document.getElementById('defmis-messages');
            messagesContainer.innerHTML = `
                <div class="defmis-message defmis-message-admin" style="
                    background: white;
                    padding: 10px 12px;
                    border-radius: 18px;
                    margin-bottom: 10px;
                    max-width: 80%;
                    font-size: 14px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    ${widgetConfig?.welcome_message || 'Hi there! How can we help you today?'}
                </div>
            `;

            messages.forEach(message => {
                const attachmentUrl = message.attachment ? 
                    (message.attachment.startsWith('http') ? message.attachment : `${config.apiUrl}${message.attachment}`) : 
                    null;
                addMessage(message.content, message.sender_type, message.sender_name || 'Admin', false, attachmentUrl);
            });

            scrollToBottom();
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    };

    // Initialize WebSocket connection
    const initWebSocket = () => {
        const wsScheme = config.apiUrl.startsWith('https') ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://${new URL(config.apiUrl).host}/ws/chat/${config.customerId}/`;

        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            isConnected = true;
            updateConnectionStatus('Connected');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Client widget received WebSocket message:', data);  // Debug log
            
            if (data.type === 'chat_message') {
                // Display messages from admin or system (automated responses)
                if (data.sender_type === 'admin' || data.sender_type === 'system') {
                    console.log('Displaying admin/system message:', data.message);  // Debug log
                    const attachmentUrl = data.attachment_url || null;
                    addMessage(data.message, data.sender_type, data.sender_name, true, attachmentUrl);
                    
                    // Show notification if widget is closed
                    if (!isWidgetOpen) {
                        showNewMessageNotification(data.sender_name, data.message);
                        incrementUnreadCounter();
                    }
                }
            } else if (data.type === 'conversation_closed') {
                handleConversationClosed(data.closed_by);
            } else if (data.type === 'conversation_reopened') {
                handleConversationReopened(data.reopened_by);
            }
        };

        socket.onclose = () => {
            isConnected = false;
            updateConnectionStatus('Disconnected');
            // Try to reconnect after 3 seconds
            setTimeout(initWebSocket, 3000);
        };

        socket.onerror = () => {
            updateConnectionStatus('Connection Error');
        };
    };

    // Update connection status
    const updateConnectionStatus = (status) => {
        const statusElement = document.getElementById('defmis-connection-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    };

    // Show customer info form
    const showCustomerForm = () => {
        const customerForm = document.getElementById('defmis-customer-form');
        const chatInput = document.getElementById('defmis-chat-input');
        
        if (customerForm) customerForm.style.display = 'block';
        if (chatInput) chatInput.style.display = 'none';
    };

    // Show chat interface
    const showChatInterface = () => {
        const customerForm = document.getElementById('defmis-customer-form');
        const chatInput = document.getElementById('defmis-chat-input');
        
        if (customerForm) customerForm.style.display = 'none';
        if (chatInput) chatInput.style.display = 'block';
    };

    // Handle customer form submission
    const handleCustomerFormSubmit = async () => {
        const nameInput = document.getElementById('defmis-customer-name');
        const emailInput = document.getElementById('defmis-customer-email');
        
        const name = nameInput?.value.trim();
        const email = emailInput?.value.trim();
        
        if (!name || !email) {
            alert('Please enter both your name and email address.');
            return;
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address.');
            return;
        }
        
        // Store customer info
        config.customerName = name;
        config.customerEmail = email;
        localStorage.setItem('defmis_customer_name', name);
        localStorage.setItem('defmis_customer_email', email);
        
        // Initialize chat session
        try {
            await initChatSession();
            showChatInterface();
            initWebSocket();
            
            // Focus on message input
            const messageInput = document.getElementById('defmis-message-input');
            if (messageInput) {
                messageInput.focus();
            }
        } catch (error) {
            console.error('Error starting chat session:', error);
            alert('Error starting chat session. Please try again.');
        }
    };

    // Set up event listeners
    const setupEventListeners = () => {
        const toggle = document.getElementById('defmis-chat-toggle');
        const window = document.getElementById('defmis-chat-window');
        const chatIcon = document.getElementById('defmis-chat-icon');
        const closeIcon = document.getElementById('defmis-close-icon');
        
        // Toggle chat window
        toggle.addEventListener('click', () => {
            const wasVisible = window.style.display === 'flex';
            isWidgetOpen = !wasVisible;
            
            window.style.display = wasVisible ? 'none' : 'flex';
            chatIcon.style.display = wasVisible ? 'block' : 'none';
            closeIcon.style.display = wasVisible ? 'none' : 'block';

            if (!wasVisible) {
                // Clear unread counter when opening
                clearUnreadCounter();
                
                // Focus on appropriate input based on current view
                if (config.customerName && config.customerEmail) {
                    const messageInput = document.getElementById('defmis-message-input');
                    if (messageInput) messageInput.focus();
                } else {
                    const nameInput = document.getElementById('defmis-customer-name');
                    if (nameInput) nameInput.focus();
                }
            }
        });

        // Customer form event listeners
        const startChatButton = document.getElementById('defmis-start-chat-button');
        const nameInput = document.getElementById('defmis-customer-name');
        const emailInput = document.getElementById('defmis-customer-email');
        
        if (startChatButton) {
            startChatButton.addEventListener('click', handleCustomerFormSubmit);
        }
        
        // Enter key on form inputs
        [nameInput, emailInput].forEach(input => {
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        handleCustomerFormSubmit();
                    }
                });
            }
        });

        // Chat message event listeners
        const input = document.getElementById('defmis-message-input');
        const sendButton = document.getElementById('defmis-send-button');
        const closeButton = document.getElementById('defmis-close-conversation-button');
        const newConversationButton = document.getElementById('defmis-new-conversation-button');

        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }

        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', closeConversation);
        }

        if (newConversationButton) {
            newConversationButton.addEventListener('click', startNewConversation);
        }

        // File attachment event listeners
        const attachmentButton = document.getElementById('defmis-attachment-button');
        const fileInput = document.getElementById('defmis-file-input');
        const removeFileButton = document.getElementById('defmis-remove-file');

        if (attachmentButton) {
            attachmentButton.addEventListener('click', () => {
                fileInput.click();
            });
        }

        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect);
        }

        if (removeFileButton) {
            removeFileButton.addEventListener('click', removeSelectedFile);
        }
    };

    // Handle file selection
    let selectedFile = null;

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('File size exceeds 10MB limit. Please choose a smaller file.');
            event.target.value = '';
            return;
        }

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf', 
                             'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            alert('File type not allowed. Please upload images, PDF, Word, Excel, or text files.');
            event.target.value = '';
            return;
        }

        selectedFile = file;
        showFilePreview(file);
    };

    const showFilePreview = (file) => {
        const preview = document.getElementById('defmis-file-preview');
        const fileName = document.getElementById('defmis-file-name');
        
        const size = file.size < 1024 * 1024 ? 
            (file.size / 1024).toFixed(1) + ' KB' : 
            (file.size / (1024 * 1024)).toFixed(1) + ' MB';
        
        fileName.textContent = `📎 ${file.name} (${size})`;
        preview.style.display = 'block';
    };

    const removeSelectedFile = () => {
        selectedFile = null;
        document.getElementById('defmis-file-input').value = '';
        document.getElementById('defmis-file-preview').style.display = 'none';
    };

    const uploadFile = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('customer_id', config.customerId);
        formData.append('sender_name', config.customerName || 'Customer');

        try {
            const response = await fetch(`${config.apiUrl}/chat/api/chat/upload/`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                return data;
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            throw error;
        }
    };

    // Send message
    const sendMessage = async () => {
        const input = document.getElementById('defmis-message-input');
        const message = input.value.trim();

        // Check if there's a file to send
        if (selectedFile) {
            try {
                // Show uploading message
                addMessage('📎 Uploading file...', 'customer', config.customerName || 'You', true);
                
                // Upload file
                const uploadData = await uploadFile(selectedFile);
                
                // Send message with file info via WebSocket
                const fileMessage = `📎 ${selectedFile.name}`;
                
                if (socket && isConnected) {
                    socket.send(JSON.stringify({
                        type: 'chat_message',
                        message: message || fileMessage,
                        sender_type: 'customer',
                        sender_name: config.customerName || 'Customer',
                        attachment_path: uploadData.attachment_path,  // Send path for DB storage
                        attachment_url: uploadData.attachment_url      // Send URL for display
                    }));
                }
                
                // Remove file preview
                removeSelectedFile();
                input.value = '';
                
            } catch (error) {
                alert('Error uploading file. Please try again.');
                console.error('Upload error:', error);
            }
            return;
        }

        if (!message) return;

        // Add message to UI immediately
        addMessage(message, 'customer', config.customerName || 'You', true);
        input.value = '';

        // Send via WebSocket if connected
        if (socket && isConnected) {
            socket.send(JSON.stringify({
                type: 'chat_message',
                message: message,
                sender_type: 'customer',
                sender_name: config.customerName || 'Customer'
            }));
        } else {
            // Fallback to HTTP API
            fetch(`${config.apiUrl}/chat/api/chat/message/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_id: config.customerId,
                    message: message,
                    sender_type: 'customer',
                    sender_name: config.customerName || 'Customer'
                })
            }).catch(error => {
                console.error('Error sending message:', error);
            });
        }
    };

    // Add message to UI
    const addMessage = (content, senderType, senderName, animate = false, attachmentUrl = null) => {
        const messagesContainer = document.getElementById('defmis-messages');
        const isCustomer = senderType === 'customer';
        const isSystem = senderType === 'system';
        const isAdmin = senderType === 'admin';

        const messageDiv = document.createElement('div');
        messageDiv.className = `defmis-message defmis-message-${senderType}`;
        
        let backgroundColor, textColor, marginLeft, marginRight, textAlign, fontStyle;
        
        if (isSystem) {
            backgroundColor = '#f8f9fa';
            textColor = '#6c757d';
            marginLeft = 'auto';
            marginRight = 'auto';
            textAlign = 'center';
            fontStyle = 'italic';
        } else if (isCustomer) {
            backgroundColor = '#007bff';
            textColor = 'white';
            marginLeft = 'auto';
            marginRight = '0';
            textAlign = 'left';
            fontStyle = 'normal';
        } else {
            backgroundColor = 'white';
            textColor = 'black';
            marginLeft = '0';
            marginRight = 'auto';
            textAlign = 'left';
            fontStyle = 'normal';
        }

        messageDiv.style.cssText = `
            background: ${backgroundColor};
            color: ${textColor};
            padding: 10px 12px;
            border-radius: 18px;
            margin-bottom: 10px;
            max-width: ${isSystem ? '90%' : '80%'};
            font-size: ${isSystem ? '12px' : '14px'};
            margin-left: ${marginLeft};
            margin-right: ${marginRight};
            text-align: ${textAlign};
            font-style: ${fontStyle};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ${isSystem ? 'border: 1px solid #e9ecef;' : ''}
            ${animate ? 'animation: slideIn 0.3s ease;' : ''}
        `;

        // Create message content with sender name for admin messages and handle attachments
        let messageContent = '';
        
        if (isAdmin && senderName && senderName !== 'Admin') {
            messageContent = `
                <div style="font-weight: 600; font-size: 11px; color: #666; margin-bottom: 4px;">
                    ${senderName}
                </div>
                <div>${content}</div>
            `;
        } else {
            messageContent = content;
        }

        // Add attachment preview if present
        if (attachmentUrl) {
            const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(attachmentUrl);
            
            if (isImage) {
                messageContent += `
                    <div style="margin-top: 8px;">
                        <a href="${attachmentUrl}" target="_blank">
                            <img src="${attachmentUrl}" style="max-width: 200px; max-height: 150px; border-radius: 8px; cursor: pointer;" />
                        </a>
                    </div>
                `;
            } else {
                const fileName = attachmentUrl.split('/').pop();
                messageContent += `
                    <div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.1); border-radius: 8px;">
                        <a href="${attachmentUrl}" target="_blank" style="color: ${isCustomer ? 'white' : '#007bff'}; text-decoration: none;">
                            📎 ${fileName}
                        </a>
                    </div>
                `;
            }
        }

        messageDiv.innerHTML = messageContent;
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    };

    // Scroll to bottom of messages
    const scrollToBottom = () => {
        const messagesContainer = document.getElementById('defmis-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    // Close conversation
    const closeConversation = () => {
        if (confirm('Are you sure you want to end this conversation?')) {
            // Send close message via WebSocket if connected
            if (socket && isConnected) {
                socket.send(JSON.stringify({
                    type: 'close_conversation',
                    sender_name: config.customerName || 'Customer'
                }));
            } else {
                // Fallback to HTTP API
                fetch(`${config.apiUrl}/chat/api/admin/session/${chatSession.id}/status/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status: 'closed'
                    })
                }).then(() => {
                    handleConversationClosed(config.customerName || 'Customer');
                }).catch(error => {
                    console.error('Error closing conversation:', error);
                });
            }
        }
    };

    // Handle conversation closed
    const handleConversationClosed = (closedBy) => {
        const chatInput = document.getElementById('defmis-chat-input');
        const conversationClosed = document.getElementById('defmis-conversation-closed');
        const closedMessage = document.getElementById('defmis-closed-message');
        
        if (chatInput) chatInput.style.display = 'none';
        if (conversationClosed) conversationClosed.style.display = 'block';
        if (closedMessage) {
            closedMessage.textContent = `This conversation was closed by ${closedBy}.`;
        }

        // Add system message to chat
        addMessage(`Conversation closed by ${closedBy}`, 'system', 'System', true);
        
        // Close WebSocket connection
        if (socket) {
            socket.close();
        }
    };

    // Handle conversation reopened
    const handleConversationReopened = (reopenedBy) => {
        const chatInput = document.getElementById('defmis-chat-input');
        const conversationClosed = document.getElementById('defmis-conversation-closed');
        
        if (chatInput) chatInput.style.display = 'block';
        if (conversationClosed) conversationClosed.style.display = 'none';

        // Add system message to chat
        addMessage(`Conversation reopened by ${reopenedBy}`, 'system', 'System', true);
        
        // Reconnect WebSocket if needed
        if (!socket || socket.readyState === WebSocket.CLOSED) {
            initWebSocket();
        }
        
        // Focus on message input
        const messageInput = document.getElementById('defmis-message-input');
        if (messageInput) {
            messageInput.focus();
        }
    };

    // Start new conversation
    const startNewConversation = () => {
        // Clear stored conversation data
        localStorage.removeItem('defmis_customer_id');
        
        // Generate new customer ID
        config.customerId = 'customer_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('defmis_customer_id', config.customerId);
        
        // Reset chat session
        chatSession = null;
        
        // Clear messages
        const messagesContainer = document.getElementById('defmis-messages');
        messagesContainer.innerHTML = `
            <div class="defmis-message defmis-message-admin" style="
                background: white;
                padding: 10px 12px;
                border-radius: 18px;
                margin-bottom: 10px;
                max-width: 80%;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                ${widgetConfig?.welcome_message || 'Hi there! How can we help you today?'}
            </div>
        `;
        
        // Show chat input and hide closed message
        const chatInput = document.getElementById('defmis-chat-input');
        const conversationClosed = document.getElementById('defmis-conversation-closed');
        
        if (chatInput) chatInput.style.display = 'block';
        if (conversationClosed) conversationClosed.style.display = 'none';
        
        // Initialize new chat session and WebSocket
        initChatSession().then(() => {
            initWebSocket();
            const messageInput = document.getElementById('defmis-message-input');
            if (messageInput) messageInput.focus();
        });
    };

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        
        #defmis-chat-toggle:hover {
            transform: scale(1.05);
        }
        
        #defmis-chat-toggle.has-notifications {
            animation: bounce 2s infinite;
        }
        
        #defmis-send-button:hover {
            opacity: 0.8;
        }
        
        #defmis-message-input:focus,
        #defmis-customer-name:focus,
        #defmis-customer-email:focus {
            border-color: ${widgetConfig?.primary_color || '#007bff'};
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }
        
        #defmis-start-chat-button:hover {
            opacity: 0.9;
        }
        
        #defmis-start-chat-button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        
        #defmis-notification-badge {
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(style);

    // Show browser notification for new message
    const showNewMessageNotification = (senderName, message) => {
        // Throttle notifications to prevent spam
        const now = Date.now();
        if (now - lastNotificationTime < 3000) return; // 3 second throttle
        lastNotificationTime = now;
        
        // Check if notifications are supported and allowed
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                const notification = new Notification(`New message from ${senderName}`, {
                    body: message.length > 50 ? message.substring(0, 50) + '...' : message,
                    icon: `${config.apiUrl}/static/images/logo.png`,
                    badge: `${config.apiUrl}/static/images/logo.png`,
                    tag: 'defmis-chat',
                    renotify: false,
                    requireInteraction: false
                });
                
                // Auto close after 5 seconds
                setTimeout(() => {
                    notification.close();
                }, 5000);
                
                // Open widget when notification is clicked
                notification.onclick = () => {
                    window.focus();
                    const chatWindow = document.getElementById('defmis-chat-window');
                    const toggle = document.getElementById('defmis-chat-toggle');
                    if (chatWindow && toggle && chatWindow.style.display !== 'flex') {
                        toggle.click();
                    }
                    notification.close();
                };
            } else if (Notification.permission === 'default') {
                // Request permission
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        showNewMessageNotification(senderName, message);
                    }
                });
            }
        }
    };

    // Increment unread message counter
    const incrementUnreadCounter = () => {
        unreadCount++;
        updateNotificationBadge();
    };

    // Clear unread message counter
    const clearUnreadCounter = () => {
        unreadCount = 0;
        updateNotificationBadge();
    };

    // Update notification badge display
    const updateNotificationBadge = () => {
        const badge = document.getElementById('defmis-notification-badge');
        const toggle = document.getElementById('defmis-chat-toggle');
        
        if (badge && toggle) {
            if (unreadCount > 0) {
                badge.style.display = 'flex';
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount.toString();
                toggle.classList.add('has-notifications');
            } else {
                badge.style.display = 'none';
                toggle.classList.remove('has-notifications');
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }

})();