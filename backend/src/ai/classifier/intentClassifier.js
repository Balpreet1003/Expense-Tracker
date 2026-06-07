const { postChatCompletion, GEMINI_MODEL } = require('../../services/gemini.service');
const { Intent, detectIntent } = require('../router/intentRouter');
const { getCachedJson, setCachedJson } = require('../../services/redis.service');
const crypto = require('crypto');

const INTENT_LABELS = Object.values(Intent);
const MIN_CONFIDENCE = 0.6;
const CACHE_TTL_SECONDS = 60 * 60 * 6;

const normalizeText = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().replace(/\s+/g, ' ').toLowerCase();
};

const hashQuery = (queryText) => crypto.createHash('sha256').update(normalizeText(queryText)).digest('hex');

const classifierSystemPrompt = [
      'You are an intent classification system.',
      'Classify the user query into exactly one category.',
      'Possible Categories:',
      'GREETING, HELP, GENERAL_CHAT, DETAILED_SUMMARY, SPENDING_ANALYSIS, SAVINGS_ADVICE, CATEGORY_ANALYSIS, TREND_ANALYSIS, CARD_ANALYSIS, TRANSACTION_ANALYSIS, INCOME_SOURCES',
      'Return ONLY a JSON object in the format: {"intent":"CATEGORY","confidence":0.92}.',
      'Do not include markdown or extra text.',
      'Definitions:',
      'GREETING: Hello, hi, hey, good morning.',
      'HELP: What can you do? Help me.',
      'DETAILED_SUMMARY: Financial summary requests (Summarize my spending, monthly report, overview of finances).',
      'SPENDING_ANALYSIS: Summaries focused on expenses/spending in a period (summarize my expenses, how much did I spend this month).',
      'SAVINGS_ADVICE: Expense reduction and budgeting (save money, reduce spending, control expenses, budget better).',
      'CATEGORY_ANALYSIS: Where am I spending the most? Category breakdown.',
      'TREND_ANALYSIS: Compare this month with last month, spending trends.',
      'CARD_ANALYSIS: Card usage and card spending analysis.',
      'TRANSACTION_ANALYSIS: Identify top, large, or unusual transactions and transaction-level insights.',
      'INCOME_SOURCES: Requests for a list/breakdown of income sources (salary, freelance, business income, earnings sources).',
      'GENERAL_CHAT: Everything else.',
].join(' ');

const extractResponseText = (response) => {
      if (typeof response?.text === 'function') {
            return response.text().trim();
      }

      const parts = response?.candidates?.[0]?.content?.parts || [];

      return parts
            .map((part) => (typeof part?.text === 'string' ? part.text : ''))
            .join('')
            .trim();
};

const normalizeIntent = (value) => {
      if (typeof value !== 'string') {
            return null;
      }

      const upper = value.trim().toUpperCase();

      return INTENT_LABELS.includes(upper) ? upper : null;
};

const parseClassifierResponse = (text) => {
      if (!text) {
            return null;
      }

      try {
            const parsed = JSON.parse(text);
            const intent = normalizeIntent(parsed.intent);
            const confidence = Number(parsed.confidence);

            if (intent) {
                  return {
                        intent,
                        confidence: Number.isFinite(confidence) ? Math.max(0, Math.min(confidence, 1)) : 0.5,
                  };
            }
      }
      catch {
            // ignore JSON parse errors
      }

      const matched = INTENT_LABELS.find((label) => text.toUpperCase().includes(label));

      if (matched) {
            return { intent: matched, confidence: 0.5 };
      }

      return null;
};

const classifyIntent = async (query) => {
      const trimmed = typeof query === 'string' ? query.trim() : '';

      if (!trimmed) {
            return { intent: Intent.GENERAL_CHAT, confidence: 1 };
      }

      const routerIntent = detectIntent(trimmed);

      const isChatIntent = (value) => value === Intent.GENERAL_CHAT || value === Intent.GREETING || value === Intent.HELP;

      // Strong rule-based intents: avoid Gemini call entirely.
      if (routerIntent === Intent.GREETING || routerIntent === Intent.HELP || routerIntent === Intent.INCOME_SOURCES) {
            return { intent: routerIntent, confidence: 1 };
      }

      // Cache reduces quota usage for repeated prompts.
      const cacheKey = `intent:${hashQuery(trimmed)}`;
      const cached = await getCachedJson(cacheKey);
      if (cached?.intent) {
            if (!isChatIntent(routerIntent) && isChatIntent(cached.intent)) {
                  // ignore stale cache that would suppress financial handling
            }
            else {
                  return cached;
            }
      }

      let response;

      try {
            response = await postChatCompletion({
                  model: GEMINI_MODEL,
                  systemInstruction: classifierSystemPrompt,
                  prompt: `User Query: ${trimmed}`,
                  generationConfig: {
                        temperature: 0,
                  },
            });
      }
      catch (error) {
            const fallback = { intent: routerIntent, confidence: 0.35 };
            await setCachedJson(cacheKey, fallback, CACHE_TTL_SECONDS);
            return fallback;
      }

      const text = extractResponseText(response);
      const parsed = parseClassifierResponse(text);

      if (!parsed) {
            const fallback = { intent: routerIntent, confidence: 0.4 };
            await setCachedJson(cacheKey, fallback, CACHE_TTL_SECONDS);
            return fallback;
      }

      if (!isChatIntent(routerIntent) && isChatIntent(parsed.intent)) {
            const forced = { intent: routerIntent, confidence: Math.max(0.7, parsed.confidence || 0) };
            await setCachedJson(cacheKey, forced, CACHE_TTL_SECONDS);
            return forced;
      }

      if (parsed.confidence < MIN_CONFIDENCE) {
            const fallback = { intent: routerIntent, confidence: parsed.confidence };
            await setCachedJson(cacheKey, fallback, CACHE_TTL_SECONDS);
            return fallback;
      }

      await setCachedJson(cacheKey, parsed, CACHE_TTL_SECONDS);
      return parsed;
};

module.exports = {
      classifyIntent,
};
