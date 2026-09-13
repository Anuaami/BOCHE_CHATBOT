document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const chatMessages = document.getElementById('chat-messages');
    const btnTTS = document.getElementById('btn-tts');
    const ttsIcon = document.getElementById('tts-icon');

    let ttsEnabled = false;
    let synth = window.speechSynthesis;

    // Toggle Voice Output (Text-To-Speech)
    btnTTS.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        if (ttsEnabled) {
            btnTTS.classList.add('active');
            ttsIcon.textContent = '🔊';
            speakText("Voice Speech Enabled! Love you all!");
        } else {
            btnTTS.classList.remove('active');
            ttsIcon.textContent = '🔇';
            if (synth) synth.cancel();
        }
    });

    // Voice synthesis function
    function speakText(text) {
        if (!ttsEnabled || !synth) return;
        synth.cancel(); // Stop any active speech
        
        // Clean text of markdown stars and emojis for smoother speech
        const cleanSpeechText = text.replace(/[*_#❤️💰📈📍🥇🤝🌐]/g, '').replace(/https?:\/\/\S+/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanSpeechText);
        utterance.rate = 1.0;
        utterance.pitch = 1.05;
        
        // Select an English voice if available
        const voices = synth.getVoices();
        const engVoice = voices.find(v => v.lang.includes('en'));
        if (engVoice) utterance.voice = engVoice;
        
        synth.speak(utterance);
    }

    // Send query to FastAPI RAG backend
    async function sendMessage(questionText) {
        const text = questionText || chatInput.value.trim();
        if (!text) return;

        // Render user message
        appendMessage('user', text);
        if (!questionText) chatInput.value = '';

        // Show typing indicator for BOCHE
        const typingId = appendTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });

            removeTypingIndicator(typingId);

            if (response.ok) {
                const data = await response.json();
                appendMessage('bot', data.answer, data.citations);
                speakText(data.answer);
            } else {
                appendMessage('bot', "Love you all! ❤️ I am temporarily updating my knowledge base. Please try asking again in a moment or call our helpline at 1800-425-4255!");
            }
        } catch (error) {
            console.error("API error:", error);
            removeTypingIndicator(typingId);
            appendMessage('bot', "Love you all! ❤️ I am currently preparing the latest knowledge database. Please ensure the backend server is running!");
        }
    }

    function appendMessage(sender, text, citations = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${sender}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'msg-avatar';
        
        if (sender === 'bot') {
            avatarDiv.innerHTML = `<img src="boche_md.png" alt="BOCHE Avatar">`;
        } else {
            avatarDiv.innerHTML = `<div style="width:100%;height:100%;background:linear-gradient(135deg, #00d2ff, #3a7bd5);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:bold;font-size:0.8rem;">YOU</div>`;
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'msg-content';

        // Basic markdown formatting convert
        let formattedText = text.replace(/\n/g, '<br>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        contentDiv.innerHTML = formattedText;

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);
        chatMessages.appendChild(msgDiv);

        // Auto-scroll
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'msg bot';
        msgDiv.id = id;

        msgDiv.innerHTML = `
            <div class="msg-avatar"><img src="boche_md.png" alt="BOCHE"></div>
            <div class="msg-content" style="color: var(--gold-bright); font-style: italic;">
                BOCHE AI is thinking & searching knowledge base...
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Event listeners
    btnSend.addEventListener('click', () => sendMessage());
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Global helper for quick prompt chips
    window.sendQuickPrompt = function(promptText) {
        sendMessage(promptText);
    };
});
