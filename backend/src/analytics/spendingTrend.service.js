const { getTrendSummary } = require('./financialAnalytics.service');

const getSpendingTrend = async ({ userId, month }) => getTrendSummary(userId, month);

module.exports = {
      getSpendingTrend,
      getTrendSummary,
};
