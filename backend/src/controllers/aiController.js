const { GoogleGenerativeAI } = require('@google/generative-ai');
const { query } = require('../config/db');
const { toTransactionResponse } = require('../utils/pgHelpers');

const formatRupees = (value) =>
      new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 2,
      }).format(Number(value || 0));

const buildFallbackReply = (transactions, prompt) => {
      if (!transactions.length) {
            return `I couldn't reach the AI service right now, and there are no transactions yet to analyze. Add a few transactions and try again.`;
      }

      const totals = transactions.reduce(
            (accumulator, transaction) => {
                  const amount = Number(transaction.amount || 0);
                  const type = String(transaction.type || '').toLowerCase();

                  if (type === 'income') {
                        accumulator.income += amount;
                  }
                  else if (type === 'expense') {
                        accumulator.expense += amount;
                        const category = transaction.category || 'Uncategorized';
                        accumulator.expenseByCategory[category] = (accumulator.expenseByCategory[category] || 0) + amount;
                  }

                  return accumulator;
            },
            {
                  income: 0,
                  expense: 0,
                  expenseByCategory: {},
            }
      );

      const topExpenseCategory = Object.entries(totals.expenseByCategory)
            .sort((left, right) => right[1] - left[1])[0];

      const recentTransactions = transactions.slice(0, 5).map((transaction) => {
            const signedAmount = String(transaction.type || '').toLowerCase() === 'expense'
                  ? `-${formatRupees(transaction.amount)}`
                  : formatRupees(transaction.amount);

            return `${transaction.type || 'transaction'} in ${transaction.category || 'Uncategorized'} for ${signedAmount}`;
      });

      const promptHint = prompt.toLowerCase();
      const balance = totals.income - totals.expense;

      let insight = `Your current balance from the available transactions is ${formatRupees(balance)}.`;

      if (promptHint.includes('spend') || promptHint.includes('expense')) {
            insight = `Your total expenses are ${formatRupees(totals.expense)}.`;
      }
      else if (promptHint.includes('income') || promptHint.includes('earn')) {
            insight = `Your total income is ${formatRupees(totals.income)}.`;
      }

      const categoryLine = topExpenseCategory
            ? `Your highest expense category is ${topExpenseCategory[0]} at ${formatRupees(topExpenseCategory[1])}.`
            : 'I do not see any expense categories yet.';

      return [
            `I could not reach the AI service, so here is a quick transaction summary instead.`,
            insight,
            categoryLine,
            `Recent transactions: ${recentTransactions.join('; ')}.`,
      ].join(' ');
};

const getModel = () => {
      const apiKey = process.env.GEMINI_API_KEY;

      if (!apiKey) {
            throw new Error('GEMINI_API_KEY is not configured');
      }

      const genAI = new GoogleGenerativeAI(apiKey);
      return genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
};

exports.analyzeTransactions = async (req, res) => {
      try {
            const prompt = typeof req.body?.prompt === 'string' ? req.body.prompt.trim() : '';

            if (!prompt) {
                  return res.status(400).json({ message: 'Prompt is required' });
            }

            const transactionsResult = await query(
                  `SELECT t.id,
                          t.user_id,
                          t.card_id,
                          t.cards,
                          t.icon,
                          t.type,
                          t.category,
                          t.amount,
                          t.date,
                          t.description,
                          t.created_at,
                          t.updated_at,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                   ORDER BY t.date DESC, t.id DESC`,
                  [req.user.id]
            );

            const transactions = transactionsResult.rows.map(toTransactionResponse);
            const model = getModel();

            const input = `
You are a financial assistant.
Here are the user's recent transactions:
${JSON.stringify(transactions, null, 2)}

User's query:
${prompt}

Please analyze or respond helpfully in a clear, concise way. Always show money in rupees format (₹).
`;

            try {
                  const result = await model.generateContent(input);
                  const response = await result.response;
                  const reply = response.text();

                  return res.json({ reply });
            }
            catch (aiError) {
                  console.error('AI service unavailable, using fallback summary:', aiError);
                  return res.json({ reply: buildFallbackReply(transactions, prompt) });
            }
      }
      catch (error) {
            console.error('AI analysis error:', error);
            return res.status(500).json({ message: 'Failed to analyze transactions' });
      }
};