const { getMonthlySummary } = require('./getMonthlySummary');
const { getCategoryBreakdown } = require('./getCategoryBreakdown');
const { getTopExpenses } = require('./getTopExpenses');
const { getExpenseTrend } = require('./getExpenseTrend');
const { getCardAnalytics } = require('./getCardAnalytics');
const { searchFinancialAdvice } = require('./searchFinancialAdvice');

const tools = {
      getMonthlySummary,
      getCategoryBreakdown,
      getTopExpenses,
      getExpenseTrend,
      getCardAnalytics,
      searchFinancialAdvice,
};

module.exports = {
      tools,
      getMonthlySummary,
      getCategoryBreakdown,
      getTopExpenses,
      getExpenseTrend,
      getCardAnalytics,
      searchFinancialAdvice,
};