const { query } = require('../config/db');
const { toTransactionResponse } = require('../utils/pgHelpers');

// Dashboard data using Transaction model
exports.getDashboardData = async (req, res) => {
    try {
        const userId = req.user.id;
        const [summaryResult, recentResult, income60Result, expense30Result] = await Promise.all([
            query(
                `SELECT
                     COALESCE(SUM(CASE WHEN LOWER(type::text) = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                     COALESCE(SUM(CASE WHEN LOWER(type::text) = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
                 FROM transactions
                 WHERE user_id = $1`,
                [userId]
            ),
            query(
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
                 ORDER BY t.date DESC, t.id DESC
                 LIMIT 5`,
                [userId]
            ),
            query(
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
                                     AND LOWER(t.type::text) = 'income'
                   AND t.date >= NOW() - INTERVAL '60 days'
                 ORDER BY t.date DESC, t.id DESC`,
                [userId]
            ),
            query(
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
                                     AND LOWER(t.type::text) = 'expense'
                   AND t.date >= NOW() - INTERVAL '30 days'
                 ORDER BY t.date DESC, t.id DESC`,
                [userId]
            ),
        ]);

        const totalIncome = Number(summaryResult.rows[0]?.total_income || 0);
        const totalExpense = Number(summaryResult.rows[0]?.total_expense || 0);
        const lastTransactions = recentResult.rows.map(toTransactionResponse);
        const last60DaysIncomeTransactions = income60Result.rows.map(toTransactionResponse);
        const last30DaysExpenseTransactions = expense30Result.rows.map(toTransactionResponse);

        const incomeLast60Days = last60DaysIncomeTransactions.reduce((sum, txn) => sum + Number(txn.amount || 0), 0);
        const expenseLast30Days = last30DaysExpenseTransactions.reduce((sum, txn) => sum + Number(txn.amount || 0), 0);

        // Final response
        res.json({
            totalBalance: totalIncome - totalExpense,
            totalIncome,
            totalExpense,
            last30DaysExpense: {
                total: expenseLast30Days,
                transactions: last30DaysExpenseTransactions,
            },
            last60DaysIncome: {
                total: incomeLast60Days,
                transactions: last60DaysIncomeTransactions,
            },
            recentTransactions: lastTransactions,
        });
    } catch (error) {
        res.status(500).json({ message: 'Server error', error });
    }
};