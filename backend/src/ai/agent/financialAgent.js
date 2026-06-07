const { Intent, detectIntent } = require('../router/intentRouter');
const {
      calculateFinancialHealthScore,
      getFinancialHealthStatus,
      generateInsights,
} = require('../../analytics/financialAnalytics.service');
const { searchFinancialAdviceDocs } = require('../../services/vector.service');
const { planTools } = require('../planner/toolPlanner');
const { createToolContext, executeTools } = require('../os/tools');

const formatCurrency = (value) => `₹${Number(value || 0).toLocaleString('en-IN')}`;
const formatPercent = (value) => `${Number(value || 0).toFixed(0)}%`;

const formatMonthKey = (value) => {
      if (typeof value !== 'string' || !/^\d{4}-\d{2}$/.test(value)) {
            return typeof value === 'string' ? value : '';
      }

      const date = new Date(`${value}-01T00:00:00.000Z`);

      if (Number.isNaN(date.getTime())) {
            return value;
      }

      return date.toLocaleString('en-US', {
            month: 'long',
            year: 'numeric',
            timeZone: 'UTC',
      });
};

const buildIncomeSourcesReply = (incomeSources) => {
      const month = formatMonthKey(incomeSources?.month || '');
      const totalIncome = Number(incomeSources?.totalIncome || 0);
      const sources = Array.isArray(incomeSources?.sources) ? incomeSources.sources : [];

      if (!sources.length) {
            return [
                  'Direct Answer',
                  month
                        ? `I couldn’t find any income entries for ${month}.`
                        : 'I couldn’t find any income entries for the selected month.',
                  '',
                  'Next Step',
                  'If you add income transactions with clear categories/descriptions (e.g., Salary, Freelance), I can list sources and amounts here.',
            ].join('\n');
      }

      const lines = sources.map((entry) => {
            const examples = Array.isArray(entry.examples) && entry.examples.length
                  ? ` (e.g., ${entry.examples.slice(0, 2).join(', ')})`
                  : '';
            return `- ${entry.source}: ${formatCurrency(entry.totalAmount)} (${formatPercent(entry.percentage)})${examples}`;
      });

      return [
            'Direct Answer',
            month ? `Income sources for ${month} (total ${formatCurrency(totalIncome)}):` : `Income sources (total ${formatCurrency(totalIncome)}):`,
            lines.join('\n'),
      ].join('\n');
};

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

const buildKnowledgeQuery = (intent, analytics) => {
      const highestCategory = typeof analytics?.highestCategory === 'string' ? analytics.highestCategory.trim() : '';

      if (intent === Intent.SAVINGS_ADVICE || intent === Intent.CATEGORY_ANALYSIS) {
            return highestCategory
                  ? `${highestCategory} expense reduction strategies`
                  : 'budgeting and saving strategies';
      }

      if (intent === Intent.TREND_ANALYSIS) {
            return highestCategory
                  ? `${highestCategory} spending trend and budgeting strategies`
                  : 'spending trend and budgeting strategies';
      }

      if (intent === Intent.CARD_ANALYSIS) {
            return 'card spending control and budgeting tips';
      }

      if (intent === Intent.SPENDING_ANALYSIS) {
            return highestCategory
                  ? `${highestCategory} spending reduction tips`
                  : 'spending reduction tips';
      }

      if (intent === Intent.TRANSACTION_ANALYSIS) {
            return highestCategory
                  ? `${highestCategory} impulse spending control strategies`
                  : 'impulse spending control strategies';
      }

      return 'personal finance budgeting advice';
};

const mergeKnowledgeDocuments = (toolResults) => {
      const merged = [];

      if (!toolResults || typeof toolResults !== 'object') {
            return merged;
      }

      const keys = Object.keys(toolResults);

      for (const key of keys) {
            if (!key.startsWith('search')) {
                  continue;
            }

            const docs = toolResults[key];

            if (!Array.isArray(docs)) {
                  continue;
            }

            for (const doc of docs) {
                  if (!doc || typeof doc !== 'object') {
                        continue;
                  }

                  if (merged.some((existing) => existing?.title && existing.title === doc.title)) {
                        continue;
                  }

                  merged.push(doc);

                  if (merged.length >= 8) {
                        return merged;
                  }
            }
      }

      return merged;
};

const buildAnalyticsFromToolResults = ({ toolResults, context }) => {
      const hasToolResult = (name) => Object.prototype.hasOwnProperty.call(toolResults || {}, name);
      const getToolValue = (name) => (toolResults && typeof toolResults === 'object' ? toolResults[name] : undefined);
      const isErrorResult = (value) => Boolean(value) && typeof value === 'object' && !Array.isArray(value) && typeof value.error === 'string';

      const overview = toolResults.getFinancialOverview || {};
      const categoryAnalysis = getToolValue('getCategoryAnalysis');
      const trend = getToolValue('getSpendingTrend');
      const cardAnalysis = getToolValue('getCardAnalysis');

      const safeCategoryAnalysis = hasToolResult('getCategoryAnalysis') && categoryAnalysis && !isErrorResult(categoryAnalysis) ? categoryAnalysis : null;
      const safeTrend = hasToolResult('getSpendingTrend') && trend && !isErrorResult(trend) ? trend : null;
      const safeCardAnalysis = hasToolResult('getCardAnalysis') && cardAnalysis && !isErrorResult(cardAnalysis) ? cardAnalysis : null;

      const incomeSources = hasToolResult('getIncomeSources') && getToolValue('getIncomeSources') && !isErrorResult(getToolValue('getIncomeSources'))
            ? getToolValue('getIncomeSources')
            : null;

      const analytics = {
            month: overview.month || context.monthKey,
            totalIncome: Number(overview.totalIncome || 0),
            totalExpense: Number(overview.totalExpense || 0),
            netCashFlow: Number(overview.netCashFlow || 0),
            savingsRate: Number(overview.savingsRate || 0),
            averageDailySpend: Number(overview.averageDailySpend || 0),
            highestCategory: safeCategoryAnalysis ? (safeCategoryAnalysis.highestCategory || 'None') : null,
            highestCategoryAmount: safeCategoryAnalysis ? Number(safeCategoryAnalysis.highestCategoryAmount || 0) : null,
            highestCategoryPercentage: safeCategoryAnalysis ? Number(safeCategoryAnalysis.highestCategoryPercentage || 0) : 0,
            spendingTrendPercentage: safeTrend ? Number(safeTrend.growthPercentage || 0) : null,
            categoryBreakdown: safeCategoryAnalysis
                  ? (Array.isArray(safeCategoryAnalysis.categoryBreakdown) ? safeCategoryAnalysis.categoryBreakdown : [])
                  : null,
            topTransactions: hasToolResult('getTopTransactions')
                  ? (Array.isArray(getToolValue('getTopTransactions')) ? getToolValue('getTopTransactions') : null)
                  : null,
            unusualTransactions: hasToolResult('getUnusualTransactions')
                  ? (Array.isArray(getToolValue('getUnusualTransactions')) ? getToolValue('getUnusualTransactions') : null)
                  : null,
            cardWiseSpending: safeCardAnalysis
                  ? (Array.isArray(safeCardAnalysis.cardWiseSpending) ? safeCardAnalysis.cardWiseSpending : [])
                  : null,
            mostUsedCard: safeCardAnalysis ? (safeCardAnalysis.mostUsedCard || null) : null,
            recurringTransactions: hasToolResult('getRecurringTransactions')
                  ? (Array.isArray(getToolValue('getRecurringTransactions')) ? getToolValue('getRecurringTransactions') : null)
                  : null,
            incomeSources,
            executedTools: Object.keys(toolResults || {}),
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

const buildFallbackReply = (analytics, knowledgeDocuments = []) => {
      const incomeSources = analytics?.incomeSources?.sources;
      const incomeSourceLines = Array.isArray(incomeSources)
            ? incomeSources
                  .slice(0, 5)
                  .map((entry) => {
                        const examples = Array.isArray(entry.examples) && entry.examples.length
                              ? ` (e.g., ${entry.examples.slice(0, 2).join(', ')})`
                              : '';
                        return `${entry.source}: ${formatCurrency(entry.totalAmount)} (${formatPercent(entry.percentage)})${examples}`;
                  })
            : [];

      const monthLabel = formatMonthKey(analytics?.month);
      const totalExpense = Number(analytics?.totalExpense || 0);
      const totalIncome = Number(analytics?.totalIncome || 0);
      const netCashFlow = Number(analytics?.netCashFlow || 0);
      const averageDailySpend = Number(analytics?.averageDailySpend || 0);
      const highestCategory = typeof analytics?.highestCategory === 'string' ? analytics.highestCategory : null;
      const highestCategoryAmount = Number(analytics?.highestCategoryAmount || 0);
      const highestCategoryPercentage = Number(analytics?.highestCategoryPercentage || 0);
      const spendingTrendPercentage = analytics?.spendingTrendPercentage;

      const directAnswerParts = [];

      if (Number(totalExpense) === 0) {
            directAnswerParts.push(monthLabel ? `No expenses were recorded in ${monthLabel}.` : 'No expenses were recorded for the selected period.');
      }
      else {
            directAnswerParts.push(monthLabel
                  ? `In ${monthLabel}, your total expenses were ${formatCurrency(totalExpense)}.`
                  : `Your total expenses were ${formatCurrency(totalExpense)}.`);

            if (averageDailySpend > 0) {
                  directAnswerParts.push(`That’s about ${formatCurrency(averageDailySpend)}/day on average.`);
            }

            if (highestCategory && highestCategory !== 'None' && highestCategoryAmount > 0) {
                  directAnswerParts.push(`Top category: ${highestCategory} at ${formatCurrency(highestCategoryAmount)} (${formatPercent(highestCategoryPercentage)}).`);
            }

            if (typeof spendingTrendPercentage === 'number' && Number.isFinite(spendingTrendPercentage) && spendingTrendPercentage !== 0) {
                  const direction = spendingTrendPercentage > 0 ? 'up' : 'down';
                  directAnswerParts.push(`Spending is ${direction} ${formatPercent(Math.abs(spendingTrendPercentage))} vs last month.`);
            }
      }

      if (totalIncome > 0) {
            directAnswerParts.push(`Net cash flow: ${formatCurrency(netCashFlow)}.`);
      }

      const directAnswerText = directAnswerParts.filter(Boolean).join(' ');

      const categoryLines = (analytics.categoryBreakdown || [])
            .slice(0, 3)
            .map((entry) => `${entry.category}: ${formatCurrency(entry.amount)} (${formatPercent(entry.percentage)})`);

      const topTransactionLines = (analytics.topTransactions || [])
            .slice(0, 3)
            .map((transaction) => `${transaction.category} - ${formatCurrency(transaction.amount)} on ${transaction.date}${transaction.description ? `, ${transaction.description}` : ''}`);

      const recommendationLines = [
            ...(analytics.insights || []).slice(0, 3),
            ...(knowledgeDocuments || []).slice(0, 2).map((doc) => doc?.content || doc?.title).filter(Boolean),
      ];

      while (recommendationLines.length < 3) {
            recommendationLines.push('Review recurring spending, set category budgets, and move surplus cash into savings');
      }

      return [
            'Direct Answer',
            incomeSourceLines.length
                  ? incomeSourceLines.map((line) => `- ${line}`).join('\n')
                  : directAnswerText || 'Here is the summary based on the available analytics.',
            '',
            'Financial Summary',
            `Income: ${formatCurrency(analytics.totalIncome)} | Expense: ${formatCurrency(analytics.totalExpense)} | Net Cash Flow: ${formatCurrency(analytics.netCashFlow)}`,
            '',
            ...(incomeSourceLines.length
                  ? [
                        'Income Sources',
                        incomeSourceLines.map((line) => `- ${line}`).join('\n'),
                        '',
                  ]
                  : []),
            'Spending Breakdown',
            categoryLines.length ? categoryLines.map((line) => `- ${line}`).join('\n') : '- No category data available',
            '',
            'Largest Transactions',
            topTransactionLines.length ? topTransactionLines.map((line) => `- ${line}`).join('\n') : '- No transaction data available',
            '',
            'Key Insights',
            (analytics.insights || []).length ? analytics.insights.map((item) => `- ${item}`).join('\n') : '- No additional insights available',
            '',
            'Recommendations',
            recommendationLines.slice(0, 3).map((item) => `- ${item}`).join('\n'),
            '',
            'Financial Health Assessment',
            `Score: ${analytics.financialHealthScore} (${analytics.financialHealthStatus})`,
      ].join('\n');
};

const runFinancialAgent = async ({ userId, prompt, intent }) => {
      const routerIntent = detectIntent(prompt);
      let resolvedIntent = intent || routerIntent;

      if (routerIntent === Intent.INCOME_SOURCES) {
            resolvedIntent = Intent.INCOME_SOURCES;
      }

      const plannedTools = await planTools({
            userQuery: prompt,
            intent: resolvedIntent,
      });

      const toolContext = createToolContext({
            userId,
            userQuery: prompt,
      });

      const toolResults = await executeTools({
            toolNames: plannedTools,
            context: toolContext,
      });

      const analytics = buildAnalyticsFromToolResults({
            toolResults,
            context: toolContext,
      });

      if (resolvedIntent === Intent.INCOME_SOURCES && analytics.incomeSources) {
            return buildIncomeSourcesReply(analytics.incomeSources);
      }

      const trendAnalysis = Object.prototype.hasOwnProperty.call(toolResults || {}, 'getSpendingTrend')
            && toolResults.getSpendingTrend
            && !toolResults.getSpendingTrend.error
            ? toolResults.getSpendingTrend
            : null;

      let knowledgeDocuments = mergeKnowledgeDocuments(toolResults);

      if (!knowledgeDocuments.length && resolvedIntent !== Intent.INCOME_SOURCES) {
            const knowledgeQuery = buildKnowledgeQuery(resolvedIntent, analytics);
            knowledgeDocuments = await searchFinancialAdviceDocs(knowledgeQuery, 5);
      }

      if (resolvedIntent === Intent.INCOME_SOURCES && analytics.incomeSources) {
            return buildIncomeSourcesReply(analytics.incomeSources);
      }

      return buildFallbackReply(analytics, knowledgeDocuments);
};

module.exports = {
      runFinancialAgent,
      buildFallbackReply,
      detectIntent,
};
