const {
      getCategorySummary,
      getFinancialAnalyticsSnapshot,
} = require('./financialAnalytics.service');

const getCategoryAnalysis = async ({ userId, month }) => getCategorySummary(userId, month);

module.exports = {
      getCategoryAnalysis,
      getCategorySummary,
      getFinancialAnalyticsSnapshot,
};
