const { query } = require('../config/db');
const { getCachedJson, setCachedJson } = require('./redis.service');
const crypto = require('crypto');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const EMBEDDING_DIMENSIONS = 1536;
const OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small';

const financialAdviceSeed = [
      {
            title: 'Reducing Food Expenses',
            category: 'expenses',
            content: 'Cook at home. Set weekly budgets. Avoid impulse ordering.',
      },
      {
            title: 'Reducing Shopping Expenses',
            category: 'expenses',
            content: 'Follow the 24 hour waiting rule. Avoid emotional purchases.',
      },
      {
            title: 'Emergency Fund Strategy',
            category: 'savings',
            content: 'Maintain 6 months of expenses in an emergency fund before increasing discretionary spending.',
      },
];

const normalizeText = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().replace(/\s+/g, ' ').toLowerCase();
};

const vectorToSqlLiteral = (embedding) => `[${embedding.map((value) => Number(value).toFixed(8)).join(',')}]`;

const toNumber = (value) => Number.isFinite(Number(value)) ? Number(value) : 0;

const hashQuery = (queryText) => crypto.createHash('sha256').update(normalizeText(queryText)).digest('hex');

const tokenize = (text) => normalizeText(text).match(/[a-z0-9]+/g) || [];

const localEmbedding = (text) => {
      const embedding = new Array(EMBEDDING_DIMENSIONS).fill(0);
      const tokens = tokenize(text);

      if (!tokens.length) {
            return embedding;
      }

      for (const token of tokens) {
            let hash = 2166136261;

            for (let index = 0; index < token.length; index += 1) {
                  hash ^= token.charCodeAt(index);
                  hash = Math.imul(hash, 16777619);
            }

            const slot = Math.abs(hash) % EMBEDDING_DIMENSIONS;
            embedding[slot] += 1;
      }

      const magnitude = Math.sqrt(embedding.reduce((sum, value) => sum + value * value, 0)) || 1;

      return embedding.map((value) => value / magnitude);
};

const embedText = async (text) => {
      const normalizedText = normalizeText(text);

      if (!normalizedText) {
            return new Array(EMBEDDING_DIMENSIONS).fill(0);
      }

      const apiKey = process.env.OPENAI_API_KEY;

      if (apiKey) {
            try {
                  const response = await fetch('https://api.openai.com/v1/embeddings', {
                        method: 'POST',
                        headers: {
                              'Content-Type': 'application/json',
                              Authorization: `Bearer ${apiKey}`,
                        },
                        body: JSON.stringify({
                              model: OPENAI_EMBEDDING_MODEL,
                              input: normalizedText,
                              encoding_format: 'float',
                        }),
                  });

                  if (response.ok) {
                        const payload = await response.json();
                        const embedding = payload?.data?.[0]?.embedding;

                        if (Array.isArray(embedding) && embedding.length === EMBEDDING_DIMENSIONS) {
                              return embedding.map(toNumber);
                        }
                  }
            }
            catch (error) {
                  console.error('OpenAI embedding request failed, using local fallback:', error);
            }
      }

      return localEmbedding(normalizedText);
};

const seedFinancialAdviceDocs = async () => {
      for (const doc of financialAdviceSeed) {
            const combinedText = `${doc.title}. ${doc.category || ''}. ${doc.content}`;
            const embedding = await embedText(combinedText);

            await query(
                  `INSERT INTO financial_advice_docs (title, category, content, embedding)
                   VALUES ($1, $2, $3, $4::vector)
                   ON CONFLICT (title)
                   DO UPDATE SET
                         category = EXCLUDED.category,
                         content = EXCLUDED.content,
                         embedding = EXCLUDED.embedding`,
                  [doc.title, doc.category, doc.content, vectorToSqlLiteral(embedding)]
            );
      }
};

const searchFinancialAdviceDocs = async (queryText, limit = 3) => {
      const cacheKey = `advice:${hashQuery(queryText)}`;
      const cachedAdvice = await getCachedJson(cacheKey);

      if (cachedAdvice) {
            return cachedAdvice;
      }

      const embedding = await embedText(queryText);
      const vectorLiteral = vectorToSqlLiteral(embedding);

      const result = await query(
            `SELECT id, title, category, content
             FROM financial_advice_docs
             WHERE embedding IS NOT NULL
             ORDER BY embedding <=> $1::vector ASC
             LIMIT $2`,
            [vectorLiteral, limit]
      );

      const adviceDocs = result.rows;

      await setCachedJson(cacheKey, adviceDocs, CACHE_TTL_SECONDS);

      return adviceDocs;
};

module.exports = {
      seedFinancialAdviceDocs,
      searchFinancialAdviceDocs,
      embedText,
};