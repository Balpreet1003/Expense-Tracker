import moment from "moment";

export const prepareTransactionLineChartData = (data = []) => {
      // Sort by date ascending
      const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

      // Prepare arrays for income and expense, including category if present
      const incomeData = sortedData.map(item => ({
            date: moment(item.date).format("Do MMM YY"),
            amount: item.income,
            category: item.incomeCategory || null, // add category if available
      }));

      const expenseData = sortedData.map(item => ({
            date: moment(item.date).format("Do MMM YY"),
            amount: item.expense,
            category: item.expenseCategory || null, // add category if available
      }));

      return {
            incomeData,
            expenseData,
      };
}