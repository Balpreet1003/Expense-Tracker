import moment from "moment";
import { API_PATHS } from "../../../../utils/apiPaths";
import axiosInstance from "../../../../utils/axiosInstance";

export const addThousandsSeparator = (number) => {
      if(number === null || isNaN(number)) return "";

      const [integerPart, fractionPart] = String(number).split(".");
      const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

      return fractionPart? `${formattedInteger}.${fractionPart}` : formattedInteger;
};

export const prepareExpenseChartData = (data = []) => {
  const chartData = data.map((item) => {
    const date = new Date(item.date);
    const day = date.getDate();

    const suffix =
      day >= 11 && day <= 13
        ? "th"
        : day % 10 === 1
        ? "st"
        : day % 10 === 2
        ? "nd"
        : day % 10 === 3
        ? "rd"
        : "th";

    const month = date.toLocaleString("default", {
      month: "short",
    });

    return {
      amount: item.total_amount,
      date: `${day}${suffix} ${month}`,
    };
  });

  return chartData;
};