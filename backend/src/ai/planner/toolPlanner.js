const { Intent } = require('../router/intentRouter');

const MAX_TOOLS = 5;

const enforceRequiredTools = (intent, plannedTools) => {
      const tools = Array.isArray(plannedTools) ? [...plannedTools] : [];

      const ensure = (name) => {
            if (!tools.includes(name)) {
                  tools.unshift(name);
            }
      };

      switch (intent) {
            case Intent.INCOME_SOURCES:
                  ensure('getIncomeSources');
                  ensure('getFinancialOverview');
                  break;
            case Intent.CATEGORY_ANALYSIS:
                  ensure('getCategoryAnalysis');
                  ensure('getFinancialOverview');
                  break;
            case Intent.TREND_ANALYSIS:
                  ensure('getSpendingTrend');
                  ensure('getFinancialOverview');
                  break;
            case Intent.CARD_ANALYSIS:
                  ensure('getCardAnalysis');
                  ensure('getFinancialOverview');
                  break;
            case Intent.TRANSACTION_ANALYSIS:
                  ensure('getTopTransactions');
                  ensure('getFinancialOverview');
                  break;
            case Intent.SAVINGS_ADVICE:
                  ensure('getCategoryAnalysis');
                  ensure('getFinancialOverview');
                  break;
            case Intent.SPENDING_ANALYSIS:
            case Intent.DETAILED_SUMMARY:
                  ensure('getFinancialOverview');
                  break;
            default:
                  break;
      }

      return tools.slice(0, MAX_TOOLS);
};

const normalizeQuery = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().toLowerCase();
};

const hasAny = (query, phrases) => phrases.some((phrase) => query.includes(phrase));

const deterministicPlanForIntent = (intent, userQuery = '') => {
      const query = normalizeQuery(userQuery);

      switch (intent) {
            case Intent.INCOME_SOURCES:
                  return ['getFinancialOverview', 'getIncomeSources'];
            case Intent.CATEGORY_ANALYSIS:
                  return ['getFinancialOverview', 'getCategoryAnalysis'];
            case Intent.TREND_ANALYSIS:
                  return ['getFinancialOverview', 'getSpendingTrend', 'getCategoryAnalysis'];
            case Intent.CARD_ANALYSIS:
                  return ['getFinancialOverview', 'getCardAnalysis'];
            case Intent.TRANSACTION_ANALYSIS:
                  return ['getFinancialOverview', 'getTopTransactions', 'getUnusualTransactions'];
            case Intent.SAVINGS_ADVICE:
                  return ['getFinancialOverview', 'getCategoryAnalysis', 'getSpendingTrend', 'searchExpenseReductionAdvice'];
            case Intent.SPENDING_ANALYSIS:
                  if (hasAny(query, ['income sources', 'salary', 'freelance', 'business income'])) {
                        return ['getFinancialOverview', 'getIncomeSources'];
                  }

                  if (hasAny(query, ['list', 'breakdown', 'source'])) {
                        return ['getFinancialOverview', 'getCategoryAnalysis'];
                  }

                  return ['getFinancialOverview', 'getCategoryAnalysis', 'getSpendingTrend'];
            case Intent.DETAILED_SUMMARY:
                  return ['getFinancialOverview', 'getCategoryAnalysis', 'getSpendingTrend', 'getTopTransactions'];
            default:
                  return ['getFinancialOverview', 'getCategoryAnalysis'];
      }
};

const fallbackPlanForIntent = (intent) => {
      switch (intent) {
            case Intent.INCOME_SOURCES:
                  return ['getFinancialOverview', 'getIncomeSources'];
            case Intent.SAVINGS_ADVICE:
                  return ['getFinancialOverview', 'getCategoryAnalysis', 'getSpendingTrend', 'searchExpenseReductionAdvice'];
            case Intent.CATEGORY_ANALYSIS:
                  return ['getCategoryAnalysis', 'getFinancialOverview'];
            case Intent.TREND_ANALYSIS:
                  return ['getSpendingTrend', 'getFinancialOverview', 'getCategoryAnalysis'];
            case Intent.CARD_ANALYSIS:
                  return ['getCardAnalysis', 'getFinancialOverview'];
            case Intent.TRANSACTION_ANALYSIS:
                  return ['getTopTransactions', 'getUnusualTransactions', 'getCategoryAnalysis', 'getFinancialOverview'];
            case Intent.DETAILED_SUMMARY:
            case Intent.SPENDING_ANALYSIS:
            default:
                  return ['getFinancialOverview', 'getCategoryAnalysis', 'getSpendingTrend', 'getTopTransactions', 'getCardAnalysis'];
      }
};

const planTools = async ({ userQuery, intent }) => {
      const planned = deterministicPlanForIntent(intent, userQuery);
      return enforceRequiredTools(intent, planned);
};

module.exports = {
      planTools,
};
