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
        customerName: window.DEFMISChat?.customerName || '',
        customerEmail: window.DEFMISChat?.customerEmail || ''
    };

    let chatSession = null;
    let socket = null;
    let widgetConfig = null;
    let isConnected = false;

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
                ">
                    <svg id="defmis-chat-icon" width="24" height="24" fill="white" viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                    </svg>
                    <svg id="defmis-close-icon" width="24" height="24" fill="white" viewBox="0 0 24 24" style="display: none;">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
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
                    ">
                        ${widgetConfig?.name || 'Customer Support'}
                        <div id="defmis-connection-status" style="font-size: 12px; margin-top: 5px; opacity: 0.8;">
                            Connecting...
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

                    <!-- Input Area -->
                    <div style="
                        padding: 15px;
                        border-top: 1px solid #eee;
                        background: white;
                        border-radius: 0 0 10px 10px;
                    ">
                        <div style="display: flex; gap: 10px;">
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

            // Initialize chat session
            await initChatSession();

            // Set up event listeners
            setupEventListeners();

            // Initialize WebSocket
            initWebSocket();

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
                addMessage(message.content, message.sender_type, message.sender_name, false);
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
            if (data.type === 'chat_message' && data.sender_type === 'admin') {
                addMessage(data.message, data.sender_type, data.sender_name, true);
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

    // Set up event listeners
    const setupEventListeners = () => {
        const toggle = document.getElementById('defmis-chat-toggle');
        const window = document.getElementById('defmis-chat-window');
        const chatIcon = document.getElementById('defmis-chat-icon');
        const closeIcon = document.getElementById('defmis-close-icon');
        const input = document.getElementById('defmis-message-input');
        const sendButton = document.getElementById('defmis-send-button');

        // Toggle chat window
        toggle.addEventListener('click', () => {
            const isVisible = window.style.display === 'flex';
            window.style.display = isVisible ? 'none' : 'flex';
            chatIcon.style.display = isVisible ? 'block' : 'none';
            closeIcon.style.display = isVisible ? 'none' : 'block';

            if (!isVisible) {
                input.focus();
            }
        });

        // Send message on button click
        sendButton.addEventListener('click', sendMessage);

        // Send message on Enter key
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    };

    // Send message
    const sendMessage = () => {
        const input = document.getElementById('defmis-message-input');
        const message = input.value.trim();

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
    const addMessage = (content, senderType, senderName, animate = false) => {
        const messagesContainer = document.getElementById('defmis-messages');
        const isCustomer = senderType === 'customer';

        const messageDiv = document.createElement('div');
        messageDiv.className = `defmis-message defmis-message-${senderType}`;
        messageDiv.style.cssText = `
            background: ${isCustomer ? '#007bff' : 'white'};
            color: ${isCustomer ? 'white' : 'black'};
            padding: 10px 12px;
            border-radius: 18px;
            margin-bottom: 10px;
            max-width: 80%;
            font-size: 14px;
            margin-left: ${isCustomer ? 'auto' : '0'};
            margin-right: ${isCustomer ? '0' : 'auto'};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ${animate ? 'animation: slideIn 0.3s ease;' : ''}
        `;
        messageDiv.textContent = content;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    };

    // Scroll to bottom of messages
    const scrollToBottom = () => {
        const messagesContainer = document.getElementById('defmis-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        #defmis-chat-toggle:hover {
            transform: scale(1.05);
        }
        
        #defmis-send-button:hover {
            opacity: 0.8;
        }
        
        #defmis-message-input:focus {
            border-color: ${widgetConfig?.primary_color || '#007bff'};
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }
    `;
    document.head.appendChild(style);

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }

})();