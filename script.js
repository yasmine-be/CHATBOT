document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const quickReplyBtns = document.querySelectorAll('.quick-reply-btn');
    
    // Function to add a message to the chat
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerHTML = `<p>${text}</p>`;
        
        const timeDiv = document.createElement('div');
        timeDiv.classList.add('message-time');
        timeDiv.textContent = getCurrentTime();
        
        messageDiv.appendChild(contentDiv);
        timeDiv.classList.add('message-time');
        timeDiv.textContent = getCurrentTime();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to get current time in HH:MM AM/PM format
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        return `${hours}:${minutes} ${ampm}`;
    }
    
    // Function to send message to backend and get response
    async function sendToBackend(message) {
        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return "I'm having trouble connecting to the server. Please try again later.";
        }
    }
    
    // Function to process user input and generate bot response
    async function processUserInput(input) {
        input = input.trim();
        if (!input) return;
        
        addMessage(input, true);
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('message', 'bot-message');
        typingIndicator.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Get response from backend
        const response = await sendToBackend(input);
        
        // Remove typing indicator
        chatMessages.removeChild(typingIndicator);
        
        // Add bot response
        addMessage(response, false);
        
        // Add disclaimer after bot response
        setTimeout(() => {
            addMessage("Remember, I'm not a substitute for professional medical advice. If symptoms persist or worsen, please consult a doctor.", false);
        }, 1000);
    }
    
    // Event listener for send button
    sendBtn.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            userInput.value = '';
            processUserInput(message);
        }
    });
    
    // Event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                userInput.value = '';
                processUserInput(message);
            }
        }
    });
    
    // Event listeners for quick reply buttons
    quickReplyBtns.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.textContent;
            processUserInput(message);
        });
    });
    
    // Disclaimer message after 5 seconds
    setTimeout(() => {
        addMessage("Note : Ce chatbot est une démonstration et ne fournit pas de diagnostic médical. Consultez toujours un professionnel de santé pour des conseils médicaux", false);
    }, 5000);
});