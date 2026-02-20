/**
 * Claude Multi-Terminal Web Viewer
 * Real-time session viewer with collaboration features
 */

class SessionViewer {
    constructor() {
        this.ws = null;
        this.shareToken = null;
        this.userId = null;
        this.sessionId = null;
        this.accessType = 'read';
        this.participants = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;

        // DOM elements
        this.terminalOutput = document.getElementById('terminal-output');
        this.participantList = document.getElementById('participant-list');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.statusDot = document.getElementById('status-dot');
        this.statusText = document.getElementById('status-text');
        this.participantCount = document.getElementById('participant-count');
        this.accessMode = document.getElementById('access-mode');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorMessage = document.getElementById('error-message');

        this.init();
    }

    init() {
        // Get share token from URL
        const urlParams = new URLSearchParams(window.location.search);
        this.shareToken = urlParams.get('token');

        if (!this.shareToken) {
            this.showError('No share token provided in URL');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();

        // Connect to WebSocket
        this.connect();
    }

    setupEventListeners() {
        // Chat input
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.chatInput.value.trim()) {
                this.sendChatMessage(this.chatInput.value.trim());
                this.chatInput.value = '';
            }
        });

        // Sidebar tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.dataset.tab);
            });
        });

        // Window visibility change - reconnect if needed
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && (!this.ws || this.ws.readyState !== WebSocket.OPEN)) {
                this.connect();
            }
        });
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname || 'localhost';
        const port = 8765;
        const wsUrl = `${protocol}//${host}:${port}/ws`;

        this.updateStatus('connecting', 'Connecting...');

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateStatus('connected', 'Connected');
                this.joinSession();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('error', 'Connection error');
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateStatus('disconnected', 'Disconnected');
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.showError('Failed to connect to server');
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.showError('Failed to reconnect after multiple attempts');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        this.updateStatus('reconnecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        setTimeout(() => {
            this.connect();
        }, delay);
    }

    joinSession() {
        this.send({
            type: 'join',
            share_token: this.shareToken
        });
    }

    handleMessage(message) {
        console.log('Received message:', message);

        switch (message.type) {
            case 'join':
                this.handleJoinResponse(message);
                break;

            case 'user_joined':
                this.handleUserJoined(message);
                break;

            case 'user_left':
                this.handleUserLeft(message);
                break;

            case 'session_update':
                this.handleSessionUpdate(message);
                break;

            case 'cursor_move':
                this.handleCursorMove(message);
                break;

            case 'message':
                this.handleChatMessage(message);
                break;

            case 'output':
                this.handleTerminalOutput(message);
                break;

            case 'error':
                this.showError(message.error || 'An error occurred');
                break;
        }
    }

    handleJoinResponse(message) {
        if (!message.success) {
            this.showError(message.error || 'Failed to join session');
            return;
        }

        this.userId = message.user_id;
        this.sessionId = message.session_id;
        this.accessType = message.access_type;

        console.log('Joined session:', {
            userId: this.userId,
            sessionId: this.sessionId,
            accessType: this.accessType
        });

        // Update UI
        this.updateAccessMode(this.accessType);

        // Load session data
        if (message.session_data) {
            this.loadSessionData(message.session_data);
        }

        // Load participants
        if (message.participants) {
            message.participants.forEach(userId => {
                if (userId !== this.userId) {
                    this.addParticipant(userId);
                }
            });
        }

        // Hide loading overlay
        this.loadingOverlay.classList.add('hidden');
    }

    handleUserJoined(message) {
        console.log('User joined:', message.user_id);
        this.addParticipant(message.user_id);
        this.updateParticipantCount(message.participant_count);
    }

    handleUserLeft(message) {
        console.log('User left:', message.user_id);
        this.removeParticipant(message.user_id);
    }

    handleSessionUpdate(message) {
        console.log('Session update:', message.data);
        this.loadSessionData(message.data);
    }

    handleCursorMove(message) {
        // Update cursor position for user
        const userId = message.user_id;
        const position = message.position;

        // Remove old cursor
        const oldCursor = this.terminalOutput.querySelector(`[data-cursor="${userId}"]`);
        if (oldCursor) {
            oldCursor.remove();
        }

        // Add new cursor at position
        if (position) {
            this.addCursor(userId, position);
        }
    }

    handleChatMessage(message) {
        this.addChatMessage(message.user_id, message.message, message.timestamp);
    }

    handleTerminalOutput(message) {
        // Append terminal output
        const outputText = message.data || '';
        this.appendTerminalOutput(outputText);
    }

    loadSessionData(data) {
        // Load terminal output
        if (data.terminal_output) {
            this.terminalOutput.textContent = data.terminal_output;
        }

        // Scroll to bottom
        this.scrollToBottom();
    }

    appendTerminalOutput(text) {
        this.terminalOutput.textContent += text;
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.terminalOutput.parentElement.scrollTop =
            this.terminalOutput.parentElement.scrollHeight;
    }

    addParticipant(userId) {
        if (this.participants.has(userId)) {
            return;
        }

        this.participants.set(userId, {
            id: userId,
            name: this.getUserDisplayName(userId),
            joinedAt: new Date()
        });

        this.renderParticipants();
    }

    removeParticipant(userId) {
        this.participants.delete(userId);
        this.renderParticipants();

        // Remove cursor
        const cursor = this.terminalOutput.querySelector(`[data-cursor="${userId}"]`);
        if (cursor) {
            cursor.remove();
        }
    }

    renderParticipants() {
        this.participantList.innerHTML = '';

        // Add self first
        this.participantList.appendChild(
            this.createParticipantElement(this.userId, 'You', true)
        );

        // Add other participants
        this.participants.forEach((participant, userId) => {
            this.participantList.appendChild(
                this.createParticipantElement(userId, participant.name, false)
            );
        });

        this.updateParticipantCount(this.participants.size + 1);
    }

    createParticipantElement(userId, name, isSelf) {
        const li = document.createElement('li');
        li.className = 'participant-item';

        const avatar = document.createElement('div');
        avatar.className = 'participant-avatar';
        avatar.textContent = name[0].toUpperCase();
        avatar.style.background = this.getUserColor(userId);

        const info = document.createElement('div');
        info.className = 'participant-info';

        const nameEl = document.createElement('div');
        nameEl.className = 'participant-name';
        nameEl.textContent = name;

        const status = document.createElement('div');
        status.className = 'participant-status';
        status.textContent = isSelf ? 'You' : 'Viewing';

        info.appendChild(nameEl);
        info.appendChild(status);

        li.appendChild(avatar);
        li.appendChild(info);

        return li;
    }

    addCursor(userId, position) {
        // Create cursor element
        const cursor = document.createElement('span');
        cursor.className = 'cursor';
        cursor.dataset.cursor = userId;
        cursor.dataset.user = this.getUserDisplayName(userId);
        cursor.style.borderColor = this.getUserColor(userId);

        // Insert at position
        // This is simplified - real implementation would need proper text positioning
        this.terminalOutput.appendChild(cursor);
    }

    addChatMessage(userId, message, timestamp) {
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message';

        const header = document.createElement('div');
        header.className = 'chat-message-header';

        const userName = document.createElement('span');
        userName.className = 'chat-message-user';
        userName.textContent = userId === this.userId ? 'You' : this.getUserDisplayName(userId);

        const time = document.createElement('span');
        time.className = 'chat-message-time';
        time.textContent = new Date(timestamp).toLocaleTimeString();

        header.appendChild(userName);
        header.appendChild(time);

        const text = document.createElement('div');
        text.className = 'chat-message-text';
        text.textContent = message;

        messageEl.appendChild(header);
        messageEl.appendChild(text);

        this.chatMessages.appendChild(messageEl);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    sendChatMessage(message) {
        this.send({
            type: 'message',
            message: message
        });
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket not connected');
        }
    }

    updateStatus(status, text) {
        this.statusText.textContent = text;

        if (status === 'connected') {
            this.statusDot.classList.add('connected');
        } else {
            this.statusDot.classList.remove('connected');
        }
    }

    updateAccessMode(accessType) {
        this.accessMode.textContent = accessType === 'interactive' ? 'Interactive' : 'Read Only';
        this.accessMode.className = `access-badge ${accessType === 'interactive' ? 'interactive' : 'read-only'}`;
    }

    updateParticipantCount(count) {
        this.participantCount.textContent = `👥 ${count} participant${count !== 1 ? 's' : ''}`;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });

        const activeTab = document.getElementById(`${tabName}-tab`);
        if (activeTab) {
            activeTab.style.display = 'block';
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('visible');

        setTimeout(() => {
            this.errorMessage.classList.remove('visible');
        }, 5000);
    }

    getUserDisplayName(userId) {
        if (!userId) return 'Unknown';
        // Use first 8 characters of user ID as display name
        return `User ${userId.substring(0, 8)}`;
    }

    getUserColor(userId) {
        // Generate consistent color from user ID
        const hash = Array.from(userId).reduce((acc, char) => {
            return char.charCodeAt(0) + ((acc << 5) - acc);
        }, 0);

        const hue = Math.abs(hash) % 360;
        return `hsl(${hue}, 70%, 50%)`;
    }
}

// Initialize viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.viewer = new SessionViewer();
});
