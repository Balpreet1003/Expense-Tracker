const { query } = require('../config/db');
const { getCachedJson, setCachedJson } = require('./redis.service');
const crypto = require('crypto');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const EMBEDDING_DIMENSIONS = 1536;

const financialAdviceSeed = [
      {
            title: 'Reducing Food Expenses',
            category: 'food',
            content: 'Plan 3–5 repeatable meals, shop with a list, and set a weekly dining-out cap. Batch cook once a week to reduce ordering.',
      },
      {
            title: 'Reducing Shopping Expenses',
            category: 'shopping',
            content: 'Use a 24-hour rule for non-essentials, unsubscribe from promo emails, and keep a “wishlist” instead of impulse buys.',
      },
      {
            title: 'Emergency Fund Strategy',
            category: 'savings',
            content: 'Aim for 3–6 months of essential expenses. Automate a fixed transfer on payday and keep the fund in a separate, easy-access account.',
      },
      {
            title: 'Subscription Audit Playbook',
            category: 'subscriptions',
            content: 'List all recurring charges, cancel duplicates, and switch annual plans only for services you use weekly. Set a monthly subscriptions budget.',
      },
      {
            title: 'Travel Spending Control',
            category: 'travel',
            content: 'Set a per-trip budget, book early for fixed dates, and separate travel savings into a dedicated bucket so travel doesn’t hit monthly essentials.',
      },
      {
            title: 'Entertainment Budgeting',
            category: 'entertainment',
            content: 'Create a “fun money” limit and track it weekly. Prefer low-cost activities and bundle outings to reduce small frequent spends.',
      },
      {
            title: 'Utility Bills Optimization',
            category: 'bills',
            content: 'Review plans every 3–6 months, pay on time to avoid fees, and set usage reminders. Small recurring overages add up quickly.',
      },
      {
            title: 'Transportation Cost Reduction',
            category: 'transport',
            content: 'Combine errands, compare public transit vs ride-hailing, and set a weekly transport cap. Track peak days to target reductions.',
      },
      {
            title: 'Debt Paydown Priorities',
            category: 'debt',
            content: 'Pay minimums on all debts, then target the highest-interest balance first. Automate payments and avoid new balances while paying down.',
      },
      {
            title: 'Budgeting Basics (50/30/20)',
            category: 'budgeting',
            content: 'Start with a simple allocation: 50% needs, 30% wants, 20% savings/debt. Adjust based on income stability and fixed commitments.',
      },
      {
            title: 'Impulse Spending Safeguards',
            category: 'behavior',
            content: 'Remove saved cards from apps, add a small checkout friction (24-hour delay), and set an “impulse budget” to stay intentional.',
      },
      {
            title: 'Building a Savings System',
            category: 'savings',
            content: 'Automate savings immediately after income arrives. Use separate buckets for emergency, goals, and long-term savings to avoid mixing funds.',
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