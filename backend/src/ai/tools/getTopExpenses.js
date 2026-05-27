const { query } = require('../../config/db');

const getTopExpenses = async ({ userId, limit = 5 }) => {
      const safeLimit = Number.isInteger(Number(limit)) && Number(limit) > 0 ? Math.min(Number(limit), 20) : 5;

      const result = await query(
            `SELECT amount, description
             FROM transactions
             WHERE user_id = $1
               AND type = 'expense'
             ORDER BY amount DESC, date DESC, id DESC
             LIMIT $2`,
            [userId, safeLimit]
      );

      return result.rows.map((row) => ({
            amount: Number(row.amount || 0),
            description: row.description || '',
      }));
};

module.exports = {
      name: 'getTopExpenses',
      description: 'What were my largest expenses?',
      getTopExpenses,
};