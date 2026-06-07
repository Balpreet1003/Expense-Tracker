const CardModel = require('../models/Cards');
const { query } = require('../config/db');
const { normalizeMonthKey, getMonthDate } = require('../ai/tools/shared');

const getMonthRange = (month) => {
	const monthKey = normalizeMonthKey(month);
	const start = getMonthDate(monthKey);
	const end = new Date(start);
	end.setUTCMonth(end.getUTCMonth() + 1);

	return { monthKey, start, end };
};

const getUserCards = async ({ userId }) => {
	const result = await query(
		`SELECT id, user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default, created_at, updated_at
		 FROM cards
		 WHERE user_id = $1
		 ORDER BY created_at DESC, id DESC`,
		[userId]
	);

	return result.rows;
};

const getCardSpendingByMonth = async ({ userId, month = new Date() }) => {
	const { start, end } = getMonthRange(month);

	const result = await query(
		`SELECT COALESCE(MAX(c.card_name), MAX(NULLIF(t.cards, '')), CONCAT('Card ', COALESCE(t.card_id::text, 'unknown'))) AS card_name,
			  t.card_id,
			  COALESCE(SUM(t.amount), 0) AS total_spent
		 FROM transactions t
		 LEFT JOIN cards c ON c.id = t.card_id
		 WHERE t.user_id = $1
		   AND t.type = 'expense'
		   AND t.date >= $2
		   AND t.date < $3
		 GROUP BY t.card_id
		 ORDER BY total_spent DESC, card_name ASC`,
		[userId, start, end]
	);

	return result.rows;
};

module.exports = {
	CardModel,
	getUserCards,
	getCardSpendingByMonth,
};