const { query } = require('../../config/db');
const {
      getMonthlyFinancialSummary,
      getCategorySummary,
      getCardSpendingSummary,
      getTopExpenses,
      getTrendSummary,
      getUnusualTransactions,
      normalizeMonthKey,
} = require('../../analytics/financialAnalytics.service');
const { searchFinancialAdviceDocs } = require('../../services/vector.service');
const { getPreviousMonthKey } = require('../tools/shared');

const clampNumber = (value, fallback = 0) => {
      const numberValue = Number(value);
      return Number.isFinite(numberValue) ? numberValue : fallback;
};

const getNextMonthStart = (monthKey) => {
      const start = new Date(`${monthKey}-01T00:00:00.000Z`);
      start.setUTCMonth(start.getUTCMonth() + 1);
      return start;
};

const getDaysElapsedInMonth = (monthKey) => {
      const start = new Date(`${monthKey}-01T00:00:00.000Z`);
      const end = getNextMonthStart(monthKey);
      const totalDays = Math.max(1, Math.round((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)));

      const currentMonthKey = normalizeMonthKey(new Date());

      if (currentMonthKey !== monthKey) {
            return totalDays;
      }

      const now = new Date();
      const elapsedDays = Math.floor((now.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1;

      return Math.max(1, Math.min(elapsedDays, totalDays));
};

const resolveMonthKeyFromQuery = (queryText) => {
      const normalized = typeof queryText === 'string' ? queryText.toLowerCase() : '';
      const explicit = normalized.match(/\b(\d{4}-\d{2})\b/);

      if (explicit?.[1]) {
            return explicit[1];
      }

      const thisMonthKey = normalizeMonthKey(new Date());

      if (normalized.includes('this month') || normalized.includes('current month')) {
            return thisMonthKey;
      }

      if (normalized.includes('last month') || normalized.includes('previous month')) {
            return getPreviousMonthKey(thisMonthKey);
      }

      const monthMap = {
            january: 0,
            jan: 0,
            february: 1,
            feb: 1,
            march: 2,
            mar: 2,
            april: 3,
            apr: 3,
            may: 4,
            june: 5,
            jun: 5,
            july: 6,
            jul: 6,
            august: 7,
            aug: 7,
            september: 8,
            sep: 8,
            sept: 8,
            october: 9,
            oct: 9,
            november: 10,
            nov: 10,
            december: 11,
            dec: 11,
      };

      const monthMatch = normalized.match(/\b(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\b/);
      if (monthMatch?.[1]) {
            const monthIndex = monthMap[monthMatch[1]];
            const yearMatch = normalized.match(/\b(20\d{2})\b/);
            const now = new Date();
            const currentYear = now.getUTCFullYear();
            const currentMonth = now.getUTCMonth();

            let year = yearMatch?.[1] ? Number(yearMatch[1]) : currentYear;

            if (!yearMatch?.[1] && monthIndex > currentMonth) {
                  year -= 1;
            }

            const monthNumber = String(monthIndex + 1).padStart(2, '0');
            return `${year}-${monthNumber}`;
      }

      return thisMonthKey;
};

const createToolContext = ({ userId, userQuery }) => {
      const monthKey = resolveMonthKeyFromQuery(userQuery);
      const memo = new Map();

      const memoize = (key, factory) => {
            if (!memo.has(key)) {
                  memo.set(key, Promise.resolve().then(factory));
            }

            return memo.get(key);
      };

      const fetchMonthlySummary = () => memoize(`monthly:${monthKey}`, () => getMonthlyFinancialSummary(userId, monthKey));
      const fetchCategoryRaw = () => memoize(`categories:${monthKey}`, () => getCategorySummary(userId, monthKey));
      const fetchTrend = () => memoize(`trends:${monthKey}`, () => getTrendSummary(userId, monthKey));
      const fetchCards = () => memoize(`cards:${monthKey}`, () => getCardSpendingSummary(userId, monthKey));
      const fetchTop5 = () => memoize(`top:5:${monthKey}`, () => getTopExpenses(userId, monthKey, 5));
      const fetchTop20 = () => memoize(`top:20:${monthKey}`, () => getTopExpenses(userId, monthKey, 20));

      const fetchHighestCategory = async () => {
            const [summary, categories] = await Promise.all([fetchMonthlySummary(), fetchCategoryRaw()]);
            const totalExpense = clampNumber(summary?.expense);
            const highest = Array.isArray(categories) && categories.length ? categories[0] : null;
            const highestCategory = highest?.category || 'None';
            const highestCategoryAmount = clampNumber(highest?.amount);
            const highestCategoryPercentage = totalExpense > 0
                  ? Number(((highestCategoryAmount / totalExpense) * 100).toFixed(2))
                  : 0;

            return {
                  totalExpense,
                  highestCategory,
                  highestCategoryAmount,
                  highestCategoryPercentage,
            };
      };

      return {
            userId,
            userQuery,
            monthKey,
            memoize,
            fetchMonthlySummary,
            fetchCategoryRaw,
            fetchTrend,
            fetchCards,
            fetchTop5,
            fetchTop20,
            fetchHighestCategory,
      };
};

const TOOL_DEFINITIONS = [
      {
            name: 'getFinancialOverview',
            description: 'Returns overall financial position: income, expenses, net cash flow, and savings rate for the selected month.',
      },
      {
            name: 'getIncomeSources',
            description: 'Returns a list/breakdown of income sources for the selected month (grouped summary; no raw dumps).',
      },
      {
            name: 'getCategoryAnalysis',
            description: 'Returns expense category breakdown with backend-calculated percentages and highest category.',
      },
      {
            name: 'getSpendingTrend',
            description: 'Returns month-over-month expense change (current vs previous month) with growth percentage.',
      },
      {
            name: 'getCardAnalysis',
            description: 'Returns spending grouped by card with backend-calculated percentages and the most-used card.',
      },
      {
            name: 'getTopTransactions',
            description: 'Returns the top 5 highest expense transactions (sanitized fields only).',
      },
      {
            name: 'getUnusualTransactions',
            description: 'Returns abnormal/unusual expense transactions for the month (sanitized fields only).',
      },
      {
            name: 'getRecurringTransactions',
            description: 'Detects likely recurring expenses (subscriptions) using aggregation over the past months.',
      },
      {
            name: 'searchExpenseReductionAdvice',
            description: 'Retrieves advice documents focused on the dominant expense category. Never uses the raw user query.',
      },
      {
            name: 'searchBudgetingAdvice',
            description: 'Retrieves budgeting strategy documents, optionally tailored to the dominant category.',
      },
      {
            name: 'searchEmergencyFundAdvice',
            description: 'Retrieves emergency fund planning documents.',
      },
];

const TOOL_REGISTRY = {
      getFinancialOverview: async (ctx) => {
            const summary = await ctx.fetchMonthlySummary();
            const totalIncome = clampNumber(summary?.income);
            const totalExpense = clampNumber(summary?.expense);
            const netCashFlow = clampNumber(summary?.balance);
            const savingsRate = totalIncome > 0 ? Number(((netCashFlow / totalIncome) * 100).toFixed(2)) : 0;
            const averageDailySpend = Number((totalExpense / getDaysElapsedInMonth(ctx.monthKey)).toFixed(2));

            return {
                  month: ctx.monthKey,
                  totalIncome,
                  totalExpense,
                  netCashFlow,
                  savingsRate,
                  averageDailySpend,
            };
      },

      getIncomeSources: async (ctx) => {
            const start = new Date(`${ctx.monthKey}-01T00:00:00.000Z`);
            const end = getNextMonthStart(ctx.monthKey);

            const result = await query(
                  `SELECT
                        COALESCE(NULLIF(TRIM(category), ''), 'Other') AS category,
                        COALESCE(NULLIF(LOWER(TRIM(description)), ''), 'unspecified') AS description_key,
                        COUNT(*) AS occurrences,
                        COALESCE(SUM(amount), 0) AS total_amount,
                        MAX(date) AS last_received
                  FROM transactions
                  WHERE user_id = $1
                        AND type = 'income'
                        AND date >= $2
                        AND date < $3
                  GROUP BY category, description_key
                  ORDER BY total_amount DESC, occurrences DESC
                  LIMIT 50`,
                  [ctx.userId, start, end]
            );

            const rows = result.rows || [];
            const totalIncome = rows.reduce((sum, row) => sum + clampNumber(row.total_amount), 0);

            const aggregated = new Map();

            for (const row of rows) {
                  const key = `${row.category}`;
                  const existing = aggregated.get(key) || {
                        source: row.category,
                        totalAmount: 0,
                        occurrences: 0,
                        lastReceived: '',
                        examples: [],
                  };

                  existing.totalAmount += clampNumber(row.total_amount);
                  existing.occurrences += clampNumber(row.occurrences);

                  const last = row.last_received ? new Date(row.last_received).toISOString().slice(0, 10) : '';
                  if (last && (!existing.lastReceived || last > existing.lastReceived)) {
                        existing.lastReceived = last;
                  }

                  const example = row.description_key;
                  if (example && example !== 'unspecified' && existing.examples.length < 3 && !existing.examples.includes(example)) {
                        existing.examples.push(example);
                  }

                  aggregated.set(key, existing);
            }

            const sources = Array.from(aggregated.values())
                  .sort((a, b) => b.totalAmount - a.totalAmount)
                  .slice(0, 10)
                  .map((entry) => ({
                        source: entry.source,
                        totalAmount: Number(entry.totalAmount.toFixed(2)),
                        percentage: totalIncome > 0 ? Number(((entry.totalAmount / totalIncome) * 100).toFixed(2)) : 0,
                        occurrences: entry.occurrences,
                        lastReceived: entry.lastReceived,
                        examples: entry.examples,
                  }));

            return {
                  month: ctx.monthKey,
                  totalIncome: Number(totalIncome.toFixed(2)),
                  sources,
            };
      },

      getCategoryAnalysis: async (ctx) => {
            const [summary, categories] = await Promise.all([ctx.fetchMonthlySummary(), ctx.fetchCategoryRaw()]);
            const totalExpense = clampNumber(summary?.expense);
            const list = Array.isArray(categories) ? categories : [];

            const categoryBreakdown = list.map((entry) => ({
                  category: entry.category,
                  amount: clampNumber(entry.amount),
                  percentage: totalExpense > 0 ? Number(((clampNumber(entry.amount) / totalExpense) * 100).toFixed(2)) : 0,
            }));

            const highest = categoryBreakdown[0] || { category: 'None', amount: 0, percentage: 0 };

            return {
                  highestCategory: highest.category,
                  highestCategoryAmount: highest.amount,
                  highestCategoryPercentage: highest.percentage,
                  categoryBreakdown,
            };
      },

      getSpendingTrend: async (ctx) => ctx.fetchTrend(),

      getCardAnalysis: async (ctx) => {
            const [summary, cards] = await Promise.all([ctx.fetchMonthlySummary(), ctx.fetchCards()]);
            const totalExpense = clampNumber(summary?.expense);
            const list = Array.isArray(cards) ? cards : [];

            const cardWiseSpending = list.map((entry) => ({
                  cardName: entry.cardName,
                  totalSpent: clampNumber(entry.totalSpent),
                  percentage: totalExpense > 0 ? Number(((clampNumber(entry.totalSpent) / totalExpense) * 100).toFixed(2)) : 0,
            }));

            const mostUsedCard = cardWiseSpending[0] || null;

            return {
                  mostUsedCard,
                  cardWiseSpending,
            };
      },

      getTopTransactions: async (ctx) => {
            const top = await ctx.fetchTop5();
            const list = Array.isArray(top) ? top : [];

            return list.map((row) => ({
                  amount: clampNumber(row.amount),
                  category: row.category || 'Other',
                  description: row.description || '',
                  date: row.date || '',
            }));
      },

      getUnusualTransactions: async (ctx) => {
            const [summary, top20] = await Promise.all([ctx.fetchMonthlySummary(), ctx.fetchTop20()]);
            const totalExpense = clampNumber(summary?.expense);
            const list = Array.isArray(top20) ? top20 : [];

            const unusual = await getUnusualTransactions(ctx.userId, ctx.monthKey, list, totalExpense);

            return Array.isArray(unusual)
                  ? unusual.map((transaction) => ({
                        amount: clampNumber(transaction.amount),
                        category: transaction.category || 'Other',
                        description: transaction.description || '',
                        date: transaction.date || '',
                  }))
                  : [];
      },

      getRecurringTransactions: async (ctx) => {
            const sixMonthsAgo = new Date();
            sixMonthsAgo.setUTCDate(1);
            sixMonthsAgo.setUTCMonth(sixMonthsAgo.getUTCMonth() - 6);

            const result = await query(
                  `SELECT LOWER(TRIM(description)) AS description_key,
                          category,
                          COUNT(*) AS occurrences,
                          AVG(amount) AS average_amount,
                          MAX(date) AS last_seen
                   FROM transactions
                   WHERE user_id = $1
                     AND type = 'expense'
                     AND description IS NOT NULL
                     AND TRIM(description) <> ''
                     AND date >= $2
                   GROUP BY description_key, category
                   HAVING COUNT(*) >= 3
                   ORDER BY occurrences DESC, average_amount DESC
                   LIMIT 10`,
                  [ctx.userId, sixMonthsAgo]
            );

            return result.rows.map((row) => ({
                  description: row.description_key,
                  category: row.category,
                  occurrences: clampNumber(row.occurrences),
                  averageAmount: Number(clampNumber(row.average_amount).toFixed(2)),
                  lastSeen: row.last_seen ? new Date(row.last_seen).toISOString().slice(0, 10) : '',
            }));
      },

      searchExpenseReductionAdvice: async (ctx) => {
            const highest = await ctx.fetchHighestCategory();
            const queryText = highest.highestCategory && highest.highestCategory !== 'None'
                  ? `${highest.highestCategory} expense reduction strategies`
                  : 'expense reduction strategies';

            return searchFinancialAdviceDocs(queryText, 5);
      },

      searchBudgetingAdvice: async (ctx) => {
            const highest = await ctx.fetchHighestCategory();
            const queryText = highest.highestCategory && highest.highestCategory !== 'None'
                  ? `${highest.highestCategory} budgeting strategies`
                  : 'budgeting strategies';

            return searchFinancialAdviceDocs(queryText, 5);
      },

      searchEmergencyFundAdvice: async () => searchFinancialAdviceDocs('emergency fund planning', 5),
};

const executeTools = async ({ toolNames, context }) => {
      const uniqueTools = Array.from(new Set(Array.isArray(toolNames) ? toolNames : []));
      const available = uniqueTools.filter((name) => TOOL_REGISTRY[name]);

      const entries = await Promise.all(
            available.map(async (name) => {
                  try {
                        const result = await TOOL_REGISTRY[name](context);
                        return [name, result];
                  }
                  catch (error) {
                        console.error(`AI tool failed: ${name}`, error);
                        return [name, { error: error?.message || 'Tool execution failed' }];
                  }
            })
      );

      return Object.fromEntries(entries);
};

const getToolListForPlanner = () => TOOL_DEFINITIONS.map((tool) => ({
      name: tool.name,
      description: tool.description,
}));

module.exports = {
      TOOL_DEFINITIONS,
      TOOL_REGISTRY,
      createToolContext,
      executeTools,
      getToolListForPlanner,
      resolveMonthKeyFromQuery,
};
