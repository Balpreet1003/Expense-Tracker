const { GoogleGenerativeAI } = require('@google/generative-ai');

const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';

let geminiClient;
let disabledUntilMs = 0;
let disabledReason = '';

const isGeminiDisabled = () => Date.now() < disabledUntilMs;

const parseRetryDelaySeconds = (error) => {
      const details = Array.isArray(error?.errorDetails) ? error.errorDetails : [];
      const retry = details.find((item) => item && item['@type'] && String(item['@type']).includes('RetryInfo'));
      const raw = retry?.retryDelay;

      if (typeof raw !== 'string') {
            return null;
      }

      const match = raw.trim().match(/^([0-9]+(?:\.[0-9]+)?)s$/i);
      if (!match) {
            return null;
      }

      const seconds = Number(match[1]);
      return Number.isFinite(seconds) ? seconds : null;
};

const parseQuotaId = (error) => {
      const details = Array.isArray(error?.errorDetails) ? error.errorDetails : [];
      const quota = details.find((item) => item && item['@type'] && String(item['@type']).includes('QuotaFailure'));
      const violations = Array.isArray(quota?.violations) ? quota.violations : [];
      const quotaId = violations[0]?.quotaId;
      return typeof quotaId === 'string' ? quotaId : '';
};

const disableGeminiTemporarily = (reason, ttlMs) => {
      const until = Date.now() + Math.max(1000, ttlMs || 0);
      disabledUntilMs = Math.max(disabledUntilMs, until);
      disabledReason = reason || disabledReason || 'Temporarily disabled';
};

const nextUtcMidnightMs = () => {
      const now = new Date();
      const next = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1, 0, 5, 0));
      return next.getTime();
};

const toGeminiContents = (value) => {
      if (typeof value === 'string') {
            return [
                  {
                        role: 'user',
                        parts: [{ text: value }],
                  },
            ];
      }

      return value;
};

const getGeminiClient = () => {
      const apiKey = process.env.GEMINI_API_KEY;

      if (!apiKey) {
            throw new Error('GEMINI_API_KEY is not configured');
      }

      if (!geminiClient) {
            geminiClient = new GoogleGenerativeAI(apiKey);
      }

      return geminiClient;
};

const postChatCompletion = async ({
      model = GEMINI_MODEL,
      prompt,
      contents,
      systemInstruction,
      tools,
      toolConfig,
      generationConfig,
}) => {
      if (isGeminiDisabled()) {
            const secondsLeft = Math.max(1, Math.ceil((disabledUntilMs - Date.now()) / 1000));
            const error = new Error(`Gemini temporarily disabled (${disabledReason}). Try again in ~${secondsLeft}s.`);
            error.status = 429;
            throw error;
      }

      const geminiModel = getGeminiClient().getGenerativeModel({
            model,
            systemInstruction,
            tools,
            toolConfig,
      });

      const request = {};

      if (typeof contents !== 'undefined') {
            request.contents = toGeminiContents(contents);
      }
      else if (typeof prompt !== 'undefined') {
            request.contents = toGeminiContents(prompt);
      }

      if (generationConfig) {
            request.generationConfig = generationConfig;
      }

      try {
            const response = await geminiModel.generateContent(request);
            return response.response;
      }
      catch (error) {
            if (Number(error?.status) === 429) {
                  const quotaId = parseQuotaId(error);
                  const retrySeconds = parseRetryDelaySeconds(error);

                  if (quotaId && quotaId.toLowerCase().includes('perday')) {
                        const until = nextUtcMidnightMs();
                        disableGeminiTemporarily('daily quota exceeded', until - Date.now());
                  }
                  else {
                        disableGeminiTemporarily('rate limited', Math.ceil((retrySeconds || 5) * 1000));
                  }
            }

            throw error;
      }
};

module.exports = {
      postChatCompletion,
      GEMINI_MODEL,
};