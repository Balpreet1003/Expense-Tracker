const TransactionModel = require('../models/Transaction');
const { query } = require('../config/db');
const { normalizeMonthKey, getMonthDate } = require('../ai/tools/shared');

const getMonthRange = (month) => {
	const monthKey = normalizeMonthKey(month);
	const start = getMonthDate(monthKey);
	const end = new Date(start);
	end.setUTCMonth(end.getUTCMonth() + 1);

	return { monthKey, start, end };
};

const getTopExpenseTransactions = async ({ userId, month = new Date(), limit = 5 }) => {
	const safeLimit = Number.isInteger(Number(limit)) && Number(limit) > 0 ? Math.min(Number(limit), 20) : 5;
	const { start, end } = getMonthRange(month);

	const result = await query(
		`SELECT amount, category, description, date, icon, card_id, cards
		 FROM transactions
		 WHERE user_id = $1
		   AND type = 'expense'
		   AND date >= $2
		   AND date < $3
		 ORDER BY amount DESC, date DESC, id DESC
		 LIMIT $4`,
		[userId, start, end, safeLimit]
	);

	return result.rows;
};

const getMonthlyTotals = async ({ userId, month = new Date() }) => {
	const { start, end } = getMonthRange(month);

	const result = await query(
		`SELECT
			 COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
			 COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
		 FROM transactions
		 WHERE user_id = $1
		   AND date >= $2
		   AND date < $3`,
		[userId, start, end]
	);

	return result.rows[0] || { income: 0, expense: 0 };
};

module.exports = {
	TransactionModel,
	getTopExpenseTransactions,
	getMonthlyTotals,
};