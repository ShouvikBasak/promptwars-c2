const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { VertexAI } = require('@google-cloud/vertexai');

const app = express();
app.use(cors());
app.use(express.json());

const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || 'promptwars-c2';
const LOCATION = process.env.GOOGLE_CLOUD_LOCATION || 'us-central1';
const MODEL_NAME = 'gemini-1.5-flash-001';

const vertexAI = new VertexAI({ project: PROJECT_ID, location: LOCATION });
const REFUSAL_MESSAGE = "This information is not available in official Election Commission of India sources.";

function loadPrompt(filename) {
    return fs.readFileSync(path.join(__dirname, '..', 'PROMPTS', filename), 'utf8');
}

const SYSTEM_PROMPT = loadPrompt('GEMINI_SYSTEM_PROMPT.md');
const INTENT_CLASSIFIER_PROMPT = loadPrompt('INTENT_CLASSIFIER.md');
const ANSWER_GENERATOR_PROMPT = loadPrompt('ANSWER_GENERATOR.md');

app.post('/api/chat', async (req, res) => {
    try {
        const { message, history = [] } = req.body;

        // Intent Classification
        const intentModel = vertexAI.getGenerativeModel({
            model: MODEL_NAME,
            systemInstruction: { parts: [{ text: INTENT_CLASSIFIER_PROMPT }] },
            generationConfig: { responseMimeType: 'application/json' }
        });

        const intentResult = await intentModel.generateContent(message);
        let intentData = { action: 'REFUSE' };
        try {
            const text = intentResult.response.candidates[0].content.parts[0].text;
            intentData = JSON.parse(text);
        } catch (e) {
            console.error("Intent parsing failed", e);
        }

        if (intentData.action === 'REFUSE') {
            return res.json({ response: REFUSAL_MESSAGE });
        }

        // Answer Generation
        const chatModel = vertexAI.getGenerativeModel({
            model: MODEL_NAME,
            systemInstruction: { parts: [{ text: `${SYSTEM_PROMPT}\n\n${ANSWER_GENERATOR_PROMPT}` }] }
        });

        const chat = chatModel.startChat({ history });
        const answerResult = await chat.sendMessage(message);
        const answerText = answerResult.response.candidates[0].content.parts[0].text;

        res.json({ response: answerText });
    } catch (error) {
        console.error("Chat error", error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Serve frontend static files
app.use(express.static(path.join(__dirname, '..', 'frontend')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});
