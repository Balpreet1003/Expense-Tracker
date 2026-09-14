import moment from "moment";

export const prepareIncomeBarChartData = (data = []) => {
  const chartData = data.map(item => ({
    date: moment(item.date).format("Do MMM YY"),
    amount: item.amount,
  }));

  chartData.sort((a, b) => {
    const dateA = moment(a.date, "Do MMM YY");
    const dateB = moment(b.date, "Do MMM YY");
    return dateA - dateB;
  });

  return chartData;
};