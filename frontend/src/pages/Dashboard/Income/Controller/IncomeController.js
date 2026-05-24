import moment from "moment";

export const prepareIncomeBarChartData = (data= []) => {
      const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

      const chartData = sortedData.map((item) => ({
            month: moment(item?.date).format("Do MMM"),
            amount: item?.amount,
            source: item?.category,
      })); 
      
      return chartData;
}