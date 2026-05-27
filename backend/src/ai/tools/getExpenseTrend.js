const { getMonthlySummary } = require('./getMonthlySummary');
const { normalizeMonthKey, getPreviousMonthKey, getMonthLabel } = require('./shared');

const getExpenseTrend = async ({ userId, month }) => {
      const monthKey = normalizeMonthKey(month);
      const previousMonthKey = getPreviousMonthKey(monthKey);

      const [currentMonth, previousMonth] = await Promise.all([
            getMonthlySummary({ userId, month: monthKey }),
            getMonthlySummary({ userId, month: previousMonthKey }),
      ]);

      return [
            {
                  month: getMonthLabel(previousMonthKey),
                  expense: Number(previousMonth.expense || 0),
            },
            {
                  month: getMonthLabel(monthKey),
                  expense: Number(currentMonth.expense || 0),
            },
      ];
};

module.exports = {
      name: 'getExpenseTrend',
      description: 'Compare this month with last month.',
      getExpenseTrend,
};