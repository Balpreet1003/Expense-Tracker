const AdvisorSections = Object.freeze([
      'Financial Summary',
      'Spending Breakdown',
      'Largest Transactions',
      'Key Insights',
      'Recommendations',
      'Financial Health Assessment',
]);

const FinancialAnalyticsSchema = {
      totalIncome: 'number',
      totalExpense: 'number',
      netCashFlow: 'number',
      highestCategory: 'string',
      highestCategoryAmount: 'number',
      highestCategoryPercentage: 'number',
      averageDailySpend: 'number',
      spendingTrendPercentage: 'number',
      topTransactions: 'array',
      categoryBreakdown: 'array',
      cardWiseSpending: 'array',
      unusualTransactions: 'array',
      financialHealthScore: 'number',
      financialHealthStatus: 'string',
      insights: 'array',
};

module.exports = {
      AdvisorSections,
      FinancialAnalyticsSchema,
};
