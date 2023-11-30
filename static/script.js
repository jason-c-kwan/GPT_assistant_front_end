function sendMessage() {
    var input = document.getElementById("user-input");
    var message = input.value.trim();
    if (message) {
        addMessageToChatBox("You", message); // Display user's message
        showLoading(true); // Show loading indicator
        input.value = ""; // Clear input field

        fetch('/send_message', {
            method: 'POST',
            body: JSON.stringify({ 'message': message }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false); // Hide loading indicator
            if(data.error) {
                addMessageToChatBox("Error", data.error); // Display error message
            } else {
                addMessageToChatBox("GPT Assistant", data.reply); // Display GPT response
            }
        })
        .catch(error => {
            showLoading(false); // Hide loading indicator
            console.error('Error:', error);
            addMessageToChatBox("Error", "An error occurred while sending the message.");
        });
    }
}

function addMessageToChatBox(sender, message) {
    var chatBox = document.getElementById("chat-box");
    var messageElement = document.createElement("div");
    messageElement.classList.add('message');
    
    if(sender === "You") {
        messageElement.classList.add("user-message");
    } else {
        messageElement.classList.add("gpt-message");
    }

    // Convert markdown to HTML and escape HTML
    var formattedMessage = markdownToHTML(escapeHTML(message));

    // Set innerHTML based on sender
    if(sender === "You") {
        messageElement.innerHTML = `<div class="message-content user">${formattedMessage}</div>`;
    } else {
        messageElement.innerHTML = `<div class="message-content gpt">${formattedMessage}</div>`;
    }
    
    chatBox.appendChild(messageElement);

    // Apply syntax highlighting to any code blocks within the messageElement
    messageElement.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });

    // Scroll to the latest message if it's the user's message
    if(sender === "You") {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Function to escape HTML special characters to prevent HTML injection
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function markdownToHTML(text) {
    // Use 'marked' to convert markdown to HTML
    // Convert markdown to HTML using 'marked'
    let unsafeHtml = marked.parse(text);

    // Sanitize the HTML if it includes user-generated content
    let safeHtml = DOMPurify.sanitize(unsafeHtml);
    return marked.parse(safeHtml);
}



function showLoading(isLoading) {
    // Implement logic to show or hide a loading indicator
    // Example: Display a simple text message as a loading indicator
    var loadingIndicator = document.getElementById("loading-indicator");
    if (isLoading) {
        loadingIndicator.style.display = "block";
    } else {
        loadingIndicator.style.display = "none";
    }
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default action to stop from submitting a form if applicable
        sendMessage(); // Call the sendMessage function
    }
});