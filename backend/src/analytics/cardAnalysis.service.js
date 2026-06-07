const { getCardSpendingSummary } = require('./financialAnalytics.service');

const getCardAnalysis = async ({ userId, month }) => getCardSpendingSummary(userId, month);

module.exports = {
      getCardAnalysis,
      getCardSpendingSummary,
};
