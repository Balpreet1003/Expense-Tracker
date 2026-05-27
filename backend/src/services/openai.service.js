const OPENAI_CHAT_MODEL = process.env.OPENAI_CHAT_MODEL || 'gpt-4o-mini';

const postChatCompletion = async (payload) => {
      const apiKey = process.env.OPENAI_API_KEY;

      if (!apiKey) {
            throw new Error('OPENAI_API_KEY is not configured');
      }

      const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                  'Content-Type': 'application/json',
                  Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
                  model: OPENAI_CHAT_MODEL,
                  temperature: 0.2,
                  ...payload,
            }),
      });

      if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`OpenAI request failed: ${response.status} ${errorText}`);
      }

      return response.json();
};

module.exports = {
      postChatCompletion,
      OPENAI_CHAT_MODEL,
};