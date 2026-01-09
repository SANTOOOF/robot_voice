document.addEventListener('DOMContentLoaded', () => {
    const recordBtn = document.getElementById('recordBtn');
    const recordStatus = document.getElementById('recordStatus');
    const audioInput = document.getElementById('audioInput');
    const fileName = document.getElementById('fileName');
    const processBtn = document.getElementById('processBtn');
    const resultSection = document.getElementById('resultSection');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const transcriptionResult = document.getElementById('transcriptionResult');
    const intentResult = document.getElementById('intentResult');
    const confidenceResult = document.getElementById('confidenceResult');
    const historyTableBody = document.getElementById('historyTableBody');
    const emptyHistory = document.getElementById('emptyHistory');

    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;
    let isRecording = false;
    let selectedFile = null;

    // --- Microphone Recording ---
    recordBtn.addEventListener('click', async () => {
        if (!isRecording) {
            // Start Recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = () => {
                    audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    selectedFile = null; // Clear file selection if recording
                    fileName.textContent = "Audio enregistré (Micro)";
                    audioInput.value = ""; // Reset file input
                    processBtn.disabled = false;
                };

                mediaRecorder.start();
                isRecording = true;
                recordBtn.classList.add('recording-pulse', 'bg-red-500');
                recordBtn.classList.remove('bg-blue-500');
                recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
                recordStatus.textContent = "Enregistrement en cours...";
                
                // Disable file input during recording
                audioInput.disabled = true;

            } catch (err) {
                console.error("Error accessing microphone:", err);
                alert("Impossible d'accéder au microphone. Vérifiez les permissions.");
            }
        } else {
            // Stop Recording
            mediaRecorder.stop();
            isRecording = false;
            recordBtn.classList.remove('recording-pulse', 'bg-red-500');
            recordBtn.classList.add('bg-blue-500');
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            recordStatus.textContent = "Enregistrement terminé";
            
            // Re-enable file input
            audioInput.disabled = false;
        }
    });

    // --- File Upload ---
    audioInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            selectedFile = file;
            audioBlob = null; // Clear recorded audio
            fileName.textContent = file.name;
            processBtn.disabled = false;
            recordStatus.textContent = "Appuyer pour enregistrer"; // Reset record status
        }
    });

    // --- Process Audio ---
    processBtn.addEventListener('click', async () => {
        if (!audioBlob && !selectedFile) {
            alert("Veuillez d'abord enregistrer un audio ou choisir un fichier.");
            return;
        }

        // UI Updates
        processBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        resultSection.classList.add('hidden');

        const formData = new FormData();
        if (selectedFile) {
            formData.append('audio', selectedFile);
        } else {
            formData.append('audio', audioBlob, 'recording.wav');
        }

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display Results
            transcriptionResult.textContent = `"${data.transcription}"`;
            intentResult.textContent = data.intent;
            confidenceResult.textContent = `${(parseFloat(data.confidence) * 100).toFixed(0)}%`;
            
            // Color code intent
            intentResult.className = "text-2xl font-bold mr-3 " + getIntentColor(data.intent);

            resultSection.classList.remove('hidden');
            addToHistory(data.transcription, data.intent, data.confidence);

        } catch (error) {
            console.error('Error:', error);
            alert("Une erreur est survenue lors du traitement de l'audio.");
        } finally {
            loadingIndicator.classList.add('hidden');
            processBtn.disabled = false;
        }
    });

    function getIntentColor(intent) {
        switch(intent) {
            case 'AVANCER': return 'text-green-600';
            case 'STOP': return 'text-red-600';
            case 'GAUCHE': return 'text-blue-600';
            case 'DROITE': return 'text-purple-600';
            default: return 'text-gray-600';
        }
    }

    function addToHistory(text, intent, confidence) {
        emptyHistory.classList.add('hidden');
        const row = document.createElement('tr');
        row.className = "border-b hover:bg-gray-50";
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        row.innerHTML = `
            <td class="py-3 text-gray-600">${time}</td>
            <td class="py-3 font-medium text-gray-800">"${text}"</td>
            <td class="py-3"><span class="font-bold ${getIntentColor(intent)}">${intent}</span></td>
            <td class="py-3 text-gray-500">${(parseFloat(confidence) * 100).toFixed(0)}%</td>
        `;
        
        historyTableBody.prepend(row);
    }
});
