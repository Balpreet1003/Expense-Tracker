const Intent = Object.freeze({
      GREETING: 'GREETING',
      HELP: 'HELP',
      GENERAL_CHAT: 'GENERAL_CHAT',
      DETAILED_SUMMARY: 'DETAILED_SUMMARY',
      SPENDING_ANALYSIS: 'SPENDING_ANALYSIS',
      SAVINGS_ADVICE: 'SAVINGS_ADVICE',
      CATEGORY_ANALYSIS: 'CATEGORY_ANALYSIS',
      TREND_ANALYSIS: 'TREND_ANALYSIS',
      CARD_ANALYSIS: 'CARD_ANALYSIS',
      TRANSACTION_ANALYSIS: 'TRANSACTION_ANALYSIS',
      INCOME_SOURCES: 'INCOME_SOURCES',
});

const normalizeQuery = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().toLowerCase();
};

const MONTH_WORDS = [
      'january', 'jan',
      'february', 'feb',
      'march', 'mar',
      'april', 'apr',
      'may',
      'june', 'jun',
      'july', 'jul',
      'august', 'aug',
      'september', 'sep', 'sept',
      'october', 'oct',
      'november', 'nov',
      'december', 'dec',
];

const tokenize = (query) => normalizeQuery(query).split(/[^a-z0-9]+/g).filter(Boolean);

const hasTokenStartingWith = (query, prefixes) => {
      const tokens = tokenize(query);
      return tokens.some((token) => prefixes.some((prefix) => token.startsWith(prefix)));
};

const hasAnyPhrase = (query, phrases) => phrases.some((phrase) => query.includes(phrase));

const isGreeting = (query) => [
      'hi',
      'hello',
      'hey',
      'hii',
      'good morning',
      'good evening',
].includes(query);

const isFinancialQuery = (query) => {
      const financialKeywords = [
            'summary',
            'overview',
            'report',
            'expense',
            'expenses',
            'expese',
            'expeses',
            'expens',
            'income',
            'spending',
            'spend',
            'budget',
            'budgeting',
            'saving',
            'savings',
            'save money',
            'reduce expense',
            'reduce expenses',
            'cut expenses',
            'cut spending',
            'reduce spending',
            'spend less',
            'spending less',
            'overspend',
            'overspending',
            'control expense',
            'control expenses',
            'manage expenses',
            'improve my finances',
            'transaction',
            'category',
            'trend',
            'card',
            'cashflow',
            'cash flow',
            'financial',
      ];

      const monthMentioned = MONTH_WORDS.some((word) => query.includes(word));
      const financeToken = hasTokenStartingWith(query, ['expens', 'spend', 'income', 'budget', 'cash', 'transact', 'card', 'sal', 'reven']);
      const financePhrase = hasAnyPhrase(query, [
            'this month',
            'last month',
            'previous month',
            'current month',
            'my money',
            'my expenses',
            'my spending',
            'spending this month',
            'expenses this month',
            'income sources',
            'sources of income',
      ]);

      return financialKeywords.some((keyword) => query.includes(keyword)) || monthMentioned || financeToken || financePhrase;
};

const detectIntent = (query) => {
      const normalized = normalizeQuery(query);

      if (!normalized) {
            return Intent.GENERAL_CHAT;
      }

      if (isGreeting(normalized)) {
            return Intent.GREETING;
      }

      if (!isFinancialQuery(normalized)) {
            if (normalized.includes('help') || normalized.includes('what can you do') || normalized.includes('how can you help')) {
                  return Intent.HELP;
            }

            return Intent.GENERAL_CHAT;
      }

      if (
            normalized.includes('save money') ||
            normalized.includes('reduce expenses') ||
            normalized.includes('saving advice') ||
            normalized.includes('cut expenses') ||
            normalized.includes('reduce spending') ||
            normalized.includes('spend less') ||
            normalized.includes('spending less') ||
            normalized.includes('control expense') ||
            normalized.includes('control expenses') ||
            normalized.includes('manage expenses') ||
            normalized.includes('budget better')
      ) {
            return Intent.SAVINGS_ADVICE;
      }

      if (normalized.includes('where did i spend') || normalized.includes('category') || normalized.includes('where did i spend my money')) {
            return Intent.CATEGORY_ANALYSIS;
      }

      if (normalized.includes('trend') || normalized.includes('compare months') || normalized.includes('month over month')) {
            return Intent.TREND_ANALYSIS;
      }

      if (normalized.includes('card') || normalized.includes('credit card') || normalized.includes('debit card')) {
            return Intent.CARD_ANALYSIS;
      }

      if (
            normalized.includes('transaction') ||
            normalized.includes('top transactions') ||
            normalized.includes('largest transactions') ||
            normalized.includes('biggest transactions') ||
            normalized.includes('unusual transaction') ||
            normalized.includes('unusual transactions')
      ) {
            return Intent.TRANSACTION_ANALYSIS;
      }

      if (
            (normalized.includes('income') && (normalized.includes('source') || normalized.includes('sources') || normalized.includes('breakdown') || normalized.includes('list'))) ||
            normalized.includes('income sources') ||
            normalized.includes('sources of income') ||
            normalized.includes('salary breakdown') ||
            normalized.includes('earnings breakdown')
      ) {
            return Intent.INCOME_SOURCES;
      }

      if (normalized.includes('spending') || normalized.includes('expenses') || normalized.includes('budget')) {
            return Intent.SPENDING_ANALYSIS;
      }

      if (normalized.includes('summary') || normalized.includes('overview') || normalized.includes('financial report')) {
            return Intent.DETAILED_SUMMARY;
      }

      return Intent.GENERAL_CHAT;
};

module.exports = {
      Intent,
      detectIntent,
      isFinancialQuery,
};
