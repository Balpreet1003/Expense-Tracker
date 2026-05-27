const { searchFinancialAdviceDocs } = require('../../services/financialKnowledgeBaseService');

const searchFinancialAdvice = async ({ query, limit = 3 }) => searchFinancialAdviceDocs(query, limit);

module.exports = {
      name: 'searchFinancialAdvice',
      description: 'How can I save more money?',
      searchFinancialAdvice,
};