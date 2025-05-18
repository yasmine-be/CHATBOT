document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const quickReplyBtns = document.querySelectorAll('.quick-reply-btn');
    
    // Sample responses for the bot
    const botResponses = {
        "hello": "Hello! How can I assist you with your health today?",
        "headache": "Headaches can have various causes. Have you been drinking enough water? Have you taken any pain relief medication?",
        "fever": "A fever is often a sign of infection. What is your temperature? Have you experienced any other symptoms?",
        "stomach": "Stomach pain can result from many issues. Can you describe the pain? Is it sharp, dull, or cramping?",
        "allergy": "Allergy symptoms often include sneezing, itching, or rash. Have you been exposed to any potential allergens?",
        "default": "I'm not sure I understand. Could you provide more details about your symptoms?"
    };
    
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
    
    // Function to process user input and generate bot response
    function processUserInput(input) {
        input = input.toLowerCase().trim();
        let response = botResponses.default;
        
        if (input.includes('hello') || input.includes('hi')) {
            response = botResponses.hello;
        } else if (input.includes('headache')) {
            response = botResponses.headache;
        } else if (input.includes('fever') || input.includes('feverish')) {
            response = botResponses.fever;
        } else if (input.includes('stomach') || input.includes('belly')) {
            response = botResponses.stomach;
        } else if (input.includes('allergy') || input.includes('allergic')) {
            response = botResponses.allergy;
        }
        
        // Simulate typing delay
        setTimeout(() => {
            addMessage(response, false);
            
            // Add disclaimer after bot response
            setTimeout(() => {
                addMessage("Remember, I'm not a substitute for professional medical advice. If symptoms persist or worsen, please consult a doctor.", false);
            }, 1000);
        }, 1000);
    }
    
    // Event listener for send button
    sendBtn.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            processUserInput(message);
        }
    });
    
    // Event listener for Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                addMessage(message, true);
                userInput.value = '';
                processUserInput(message);
            }
        }
    });
    
    // Event listeners for quick reply buttons
    quickReplyBtns.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.textContent;
            addMessage(message, true);
            processUserInput(message);
        });
    });
    
    // Simulate microphone button click (would need additional code for actual voice recognition)
    micBtn.addEventListener('click', function() {
        addMessage("[Voice message]", true);
        setTimeout(() => {
            addMessage("I'm sorry, voice input isn't implemented in this demo. Please type your message.", false);
        }, 1000);
    });
    
    // Disclaimer message after 5 seconds
    setTimeout(() => {
        addMessage("Note: This is a demo chatbot and doesn't provide real medical diagnosis. Always consult a healthcare professional for medical advice.", false);
    }, 5000);
});