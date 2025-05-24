import './index.css'; //VERY IMPORTANT FOR WEBPACK BUNDLING CSS DONT REMOVE

document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    // IMPORTANT: Replace with your actual FULL Azure Function URL (including the code parameter)
    const AZURE_FUNCTION_URL = "YOUR_AZURE_FUNCTION_URL_HERE"; // e.g., https://mychatfuncapp.azurewebsites.net/api/ChatFunction?code=YOUR_FUNCTION_KEY

    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(`${sender}-message`);
        messageDiv.textContent = message;
        // Add a data attribute to easily identify sender and content later
        messageDiv.dataset.sender = sender;
        messageDiv.dataset.content = message;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
    }

    // New function to collect chat history
    function getChatHistory() {
        const history = [];
        const messageElements = chatWindow.querySelectorAll('.message'); // Select all message divs

        messageElements.forEach(element => {
            // Retrieve sender and content from data attributes
            const sender = element.dataset.sender;
            const content = element.dataset.content;

            // Only add if both sender and content are present (should always be with our addMessage function)
            if (sender && content) {
                history.push({
                    sender: sender,
                    message: content
                });
            }
        });
        return history;
    }

    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (userMessage === '') return;

        addMessage(userMessage, 'user'); // Add user message to display AND history
        chatInput.value = ''; // Clear input

        // Get the current chat history
        const currentHistory = getChatHistory();

        try {
            const response = await fetch(AZURE_FUNCTION_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: userMessage, // The current user message
                    history: currentHistory // The entire chat history
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            addMessage(data.reply || "Error: No reply from bot.", 'bot');

        } catch (error) {
            console.error('Error connecting to Azure Function:', error);
            addMessage("Error: Could not connect to the bot.", 'bot');
        }
    }

    sendButton.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Initialize with a bot message to be part of history from the start
    addMessage("Hello! How can I help you today?", 'bot');
});