const { query } = require('../config/db');
const {
      getCachedJson,
      setCachedJson,
      deleteByPattern,
} = require('../services/redis.service');
const {
      normalizeMonthKey,
      getMonthDate,
      getPreviousMonthKey,
} = require('../ai/tools/shared');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const toNumber = (value) => Number(value || 0);

const getNextMonthStart = (monthKey) => {
      const date = getMonthDate(monthKey);
      date.setUTCMonth(date.getUTCMonth() + 1);
      return date;
};

const getMonthRange = (monthKey) => ({
      start: getMonthDate(monthKey),
      end: getNextMonthStart(monthKey),
});

const getDaysInMonth = (monthKey) => {
      const { start, end } = getMonthRange(monthKey);
      return Math.max(1, Math.round((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)));
};

const getDaysElapsedInMonth = (monthKey) => {
      const currentMonthKey = normalizeMonthKey(new Date());

      if (currentMonthKey !== monthKey) {
            return getDaysInMonth(monthKey);
      }

      const { start } = getMonthRange(monthKey);
      const now = new Date();
      const elapsedDays = Math.floor((now.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1;

      return Math.max(1, Math.min(elapsedDays, getDaysInMonth(monthKey)));
};

const formatDate = (value) => {
      if (!value) {
            return '';
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return '';
      }

      return date.toISOString().slice(0, 10);
};

const getMonthlyFinancialSummary = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `summary:${userId}:${monthKey}`;
      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const { start, end } = getMonthRange(monthKey);

      const result = await query(
            `SELECT
                   COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                   COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
             FROM transactions
             WHERE user_id = $1
               AND date >= $2
               AND date < $3`,
            [userId, start, end]
      );

      const summary = {
            month: monthKey,
            income: toNumber(result.rows[0]?.total_income),
            expense: toNumber(result.rows[0]?.total_expense),
            balance: toNumber(result.rows[0]?.total_income) - toNumber(result.rows[0]?.total_expense),
      };

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getCategorySummary = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `categories:${userId}:${monthKey}`;
      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const { start, end } = getMonthRange(monthKey);

      const result = await query(
            `SELECT category,
                    COALESCE(SUM(amount), 0) AS total_amount
             FROM transactions
             WHERE user_id = $1
               AND type = 'expense'
               AND date >= $2
               AND date < $3
             GROUP BY category
             ORDER BY total_amount DESC, category ASC`,
            [userId, start, end]
      );

      const summary = result.rows.map((row) => ({
            category: row.category,
            amount: toNumber(row.total_amount),
      }));

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getCardSpendingSummary = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `cards:${userId}:${monthKey}`;
      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const { start, end } = getMonthRange(monthKey);

      const result = await query(
                                    `SELECT COALESCE(MAX(c.card_name), MAX(NULLIF(t.cards, '')), CONCAT('Card ', COALESCE(t.card_id::text, 'unknown'))) AS card_name,
                    t.card_id,
                    COALESCE(SUM(t.amount), 0) AS total_spent
             FROM transactions t
             LEFT JOIN cards c ON c.id = t.card_id
             WHERE t.user_id = $1
               AND t.type = 'expense'
               AND t.date >= $2
               AND t.date < $3
                                     GROUP BY t.card_id
             ORDER BY total_spent DESC, card_name ASC`,
            [userId, start, end]
      );

      const summary = result.rows.map((row) => ({
            cardId: row.card_id,
            cardName: row.card_name || `Card ${row.card_id}`,
            totalSpent: toNumber(row.total_spent),
      }));

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getTopExpenses = async (userId, month = new Date(), limit = 5) => {
      const safeLimit = Number.isInteger(Number(limit)) && Number(limit) > 0 ? Math.min(Number(limit), 20) : 5;
      const monthKey = normalizeMonthKey(month);
      const { start, end } = getMonthRange(monthKey);

      const result = await query(
            `SELECT t.amount,
                    t.category,
                    t.description,
                    t.date,
                    t.icon,
                    t.card_id,
                    COALESCE(c.card_name, t.cards, '') AS card_name
             FROM transactions t
             LEFT JOIN cards c ON c.id = t.card_id
             WHERE t.user_id = $1
               AND t.type = 'expense'
               AND t.date >= $2
               AND t.date < $3
             ORDER BY t.amount DESC, t.date DESC, t.id DESC
             LIMIT $4`,
            [userId, start, end, safeLimit]
      );

      return result.rows.map((row) => ({
            amount: toNumber(row.amount),
            category: row.category || 'Other',
            description: row.description || '',
            date: formatDate(row.date),
            cardName: row.card_name || (row.card_id ? `Card ${row.card_id}` : ''),
            icon: row.icon || '',
      }));
};

const getAverageExpenseAmount = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const { start, end } = getMonthRange(monthKey);

      const result = await query(
            `SELECT COALESCE(AVG(amount), 0) AS average_amount
             FROM transactions
             WHERE user_id = $1
               AND type = 'expense'
               AND date >= $2
               AND date < $3`,
            [userId, start, end]
      );

      return toNumber(result.rows[0]?.average_amount);
};

const getTrendSummary = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `trends:${userId}:${monthKey}`;
      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const previousMonthKey = getPreviousMonthKey(monthKey);

      const [currentMonth, previousMonth] = await Promise.all([
            getMonthlyFinancialSummary(userId, monthKey),
            getMonthlyFinancialSummary(userId, previousMonthKey),
      ]);

      const growthPercentage = previousMonth.expense > 0
            ? Number((((currentMonth.expense - previousMonth.expense) / previousMonth.expense) * 100).toFixed(2))
            : currentMonth.expense > 0
                  ? 100
                  : 0;

      const summary = {
            currentMonthExpense: currentMonth.expense,
            previousMonthExpense: previousMonth.expense,
            growthPercentage,
            currentMonth: currentMonth.month,
            previousMonth: previousMonth.month,
      };

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getUnusualTransactions = async (userId, month = new Date(), topTransactions = [], totalExpense = 0) => {
      const averageAmount = await getAverageExpenseAmount(userId, month);
      const threshold = Math.max(averageAmount * 2, totalExpense * 0.2, 0);
      const unusual = topTransactions.filter((transaction) => toNumber(transaction.amount) >= threshold);

      if (!unusual.length && topTransactions.length) {
            unusual.push(topTransactions[0]);
      }

      return unusual.slice(0, 5).map((transaction) => ({
            amount: toNumber(transaction.amount),
            category: transaction.category,
            description: transaction.description,
            date: transaction.date,
            cardName: transaction.cardName || '',
            icon: transaction.icon || '',
      }));
};

const calculateFinancialHealthScore = (analytics) => {
      const totalIncome = toNumber(analytics?.totalIncome);
      const totalExpense = toNumber(analytics?.totalExpense);
      const netCashFlow = toNumber(analytics?.netCashFlow);
      const highestCategoryPercentage = toNumber(analytics?.highestCategoryPercentage);

      let score = 57;

      if (!totalIncome) {
            score -= 15;
      }

      const savingsRate = totalIncome > 0 ? (netCashFlow / totalIncome) * 100 : 0;

      if (savingsRate > 30) {
            score += 20;
      }
      else if (savingsRate >= 20) {
            score += 15;
      }
      else if (savingsRate >= 10) {
            score += 10;
      }
      else {
            score -= 10;
      }

      if (highestCategoryPercentage > 50) {
            score -= 10;
      }

      if (totalIncome > 0 && totalExpense > totalIncome) {
            score -= 5;
      }

      return Math.max(0, Math.min(100, Math.round(score)));
};

const getFinancialHealthStatus = (score) => {
      if (score >= 90) {
            return 'Excellent';
      }

      if (score >= 75) {
            return 'Good';
      }

      if (score >= 60) {
            return 'Needs Improvement';
      }

      return 'Poor';
};

const generateInsights = (analytics) => {
      const insights = [];
      const highestCategory = analytics?.highestCategory;
      const highestCategoryPercentage = toNumber(analytics?.highestCategoryPercentage);
      const spendingTrendPercentage = toNumber(analytics?.spendingTrendPercentage);
      const unusualTransactions = Array.isArray(analytics?.unusualTransactions) ? analytics.unusualTransactions : [];
      const financialHealthScore = toNumber(analytics?.financialHealthScore);
      const totalIncome = toNumber(analytics?.totalIncome);
      const netCashFlow = toNumber(analytics?.netCashFlow);

      if (highestCategory && highestCategoryPercentage > 0) {
            insights.push(`${highestCategory} accounts for ${highestCategoryPercentage.toFixed(0)}% of total spending`);
      }

      if (spendingTrendPercentage !== 0) {
            const direction = spendingTrendPercentage > 0 ? 'increased' : 'decreased';
            insights.push(`Spending ${direction} by ${Math.abs(spendingTrendPercentage).toFixed(0)}% compared to last month`);
      }

      if (unusualTransactions.length) {
            insights.push('One transaction contributes significantly to monthly expenses');
      }

      if (!totalIncome) {
            insights.push('No income was recorded in the selected period');
      }
      else if (netCashFlow / Math.max(totalIncome, 1) < 0.2) {
            insights.push('Savings rate is below recommended threshold');
      }

      if (financialHealthScore < 75) {
            insights.push('Financial health needs attention across spending and savings habits');
      }

      while (insights.length < 3) {
            insights.push('Review recurring categories and trim non-essential spending where possible');
      }

      return insights.slice(0, 5);
};

const getFinancialAnalyticsSnapshot = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);

      const [currentMonth, previousMonth, categorySummary, cardSpendingSummary, topExpenses] = await Promise.all([
            getMonthlyFinancialSummary(userId, monthKey),
            getMonthlyFinancialSummary(userId, getPreviousMonthKey(monthKey)),
            getCategorySummary(userId, monthKey),
            getCardSpendingSummary(userId, monthKey),
            getTopExpenses(userId, monthKey, 20),
      ]);

      const totalExpense = currentMonth.expense;
      const totalIncome = currentMonth.income;
      const netCashFlow = currentMonth.balance;
      const highestCategoryEntry = categorySummary[0] || null;
      const highestCategoryAmount = toNumber(highestCategoryEntry?.amount);
      const highestCategoryPercentage = totalExpense > 0
            ? Number(((highestCategoryAmount / totalExpense) * 100).toFixed(2))
            : 0;
      const spendingTrendPercentage = previousMonth.expense > 0
            ? Number((((currentMonth.expense - previousMonth.expense) / previousMonth.expense) * 100).toFixed(2))
            : currentMonth.expense > 0
                  ? 100
                  : 0;
      const averageDailySpend = Number((totalExpense / getDaysElapsedInMonth(monthKey)).toFixed(2));

      const categoryBreakdown = categorySummary.map((entry) => ({
            category: entry.category,
            amount: entry.amount,
            percentage: totalExpense > 0 ? Number(((entry.amount / totalExpense) * 100).toFixed(2)) : 0,
      }));

      const topTransactions = topExpenses.slice(0, 5);

      const provisionalAnalytics = {
            totalIncome,
            totalExpense,
            netCashFlow,
            highestCategory: highestCategoryEntry?.category || 'None',
            highestCategoryAmount,
            highestCategoryPercentage,
            averageDailySpend,
            spendingTrendPercentage,
            topTransactions,
            categoryBreakdown,
            cardWiseSpending: cardSpendingSummary,
            unusualTransactions: [],
      };
      const unusualTransactions = await getUnusualTransactions(userId, monthKey, topExpenses, totalExpense);
      const analytics = {
            ...provisionalAnalytics,
            unusualTransactions,
      };

      const financialHealthScore = calculateFinancialHealthScore(analytics);
      const financialHealthStatus = getFinancialHealthStatus(financialHealthScore);
      const insights = generateInsights({
            ...analytics,
            financialHealthScore,
      });

      return {
            ...analytics,
            financialHealthScore,
            financialHealthStatus,
            insights,
      };
};

const invalidateUserAnalyticsCache = async (userId) => {
      await Promise.all([
            deleteByPattern(`summary:${userId}:*`),
            deleteByPattern(`categories:${userId}:*`),
            deleteByPattern(`trends:${userId}:*`),
            deleteByPattern(`cards:${userId}:*`),
      ]);
};

module.exports = {
      getMonthlyFinancialSummary,
      getCategorySummary,
      getCardSpendingSummary,
      getTopExpenses,
      getTrendSummary,
      getUnusualTransactions,
      calculateFinancialHealthScore,
      getFinancialHealthStatus,
      generateInsights,
      getFinancialAnalyticsSnapshot,
      invalidateUserAnalyticsCache,
      normalizeMonthKey,
};
