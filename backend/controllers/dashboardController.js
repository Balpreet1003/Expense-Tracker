const Transaction = require('../models/Transaction');
const { Types } = require('mongoose');

// Dashboard data using Transaction model
exports.getDashboardData = async (req, res) => {
    try {
        const userId = req.user.id;
        const userObjectId = new Types.ObjectId(String(userId));

        // Fetch all transactions for the user
        const allTransactions = await Transaction.find({ userId: { $in: [userId, userObjectId] } }).sort({ date: -1 });

        // Calculate total income and expense
        let totalIncome = 0;
        let totalExpense = 0;
        allTransactions.forEach(txn => {
            if (txn.type.toLowerCase() === 'income') totalIncome += txn.amount;
            if (txn.type.toLowerCase() === 'expense') totalExpense += txn.amount;
        });

        // Get transactions in last 60 days (income) and 30 days (expense)
        const now = new Date();
        const last60Days = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);
        const last30Days = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

        const last60DaysIncomeTransactions = allTransactions.filter(
            txn => txn.type.toLowerCase() === 'income' && txn.date >= last60Days
        );
        const last30DaysExpenseTransactions = allTransactions.filter(
            txn => txn.type.toLowerCase() === 'expense' && txn.date >= last30Days
        );

        // Sums for last 60/30 days
        const incomeLast60Days = last60DaysIncomeTransactions.reduce((sum, txn) => sum + txn.amount, 0);
        const expenseLast30Days = last30DaysExpenseTransactions.reduce((sum, txn) => sum + txn.amount, 0);

        // Last 5 transactions (income and expense, sorted by date)
        const lastTransactions = allTransactions.slice(0, 5);

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