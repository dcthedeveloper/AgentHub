/**
 * AI Chat Assistant for AgentHub - Minimal Design
 */

class ChatAssistant {
    constructor() {
        console.log('ChatAssistant: Initializing...');
        
        this.chatToggle = document.getElementById('chatToggle');
        this.chatWindow = document.getElementById('chatWindow');
        this.chatClose = document.getElementById('chatClose');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');
        
        if (!this.chatToggle) {
            console.error('ChatAssistant: chatToggle button not found!');
            return;
        }
        
        console.log('ChatAssistant: Elements found, setting up listeners...');
        this.isOpen = false;
        this.init();
    }
    
    init() {
        this.chatToggle.addEventListener('click', (e) => {
            console.log('ChatAssistant: Toggle clicked');
            e.preventDefault();
            this.toggleChat();
        });
        
        this.chatClose.addEventListener('click', (e) => {
            console.log('ChatAssistant: Close clicked');
            e.preventDefault();
            this.toggleChat();
        });
        
        this.chatSend.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        console.log('ChatAssistant: Initialized successfully');
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        this.chatWindow.classList.toggle('hidden');
        console.log('ChatAssistant: Chat toggled, isOpen =', this.isOpen);
        
        if (this.isOpen) {
            this.chatInput.focus();
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        console.log('ChatAssistant: Sending message:', message);
        
        // Add user message
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Add typing indicator
        const typingId = this.addTypingIndicator();
        
        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            console.log('ChatAssistant: Response received:', data);
            
            // Remove typing indicator
            this.removeTypingIndicator(typingId);
            
            // Add assistant response
            if (data.response) {
                this.addMessage(data.response, 'assistant');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        } catch (error) {
            console.error('ChatAssistant: Error:', error);
            this.removeTypingIndicator(typingId);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message-minimal ${sender}-message`;
        
        messageDiv.innerHTML = `
            <strong>${sender === 'user' ? 'You' : 'Assistant'}</strong>
            <p>${this.escapeHtml(text)}</p>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'chat-message-minimal assistant-message';
        typingDiv.innerHTML = `
            <strong>Assistant</strong>
            <p>Thinking...</p>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        return id;
    }
    
    removeTypingIndicator(id) {
        const element = document.getElementById(id);
        if (element) element.remove();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat when DOM is ready
console.log('chat.js: Script loaded');
document.addEventListener('DOMContentLoaded', () => {
    console.log('chat.js: DOM ready, creating ChatAssistant');
    window.chatAssistant = new ChatAssistant();
});
