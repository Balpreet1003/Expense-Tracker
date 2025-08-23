import moment from "moment";

export const validateEmail = (email) => {
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(email);
}; 

export const getInitials = (name) => {
      if (!name) return "";
      const names = name.split(" ");
      let initials = "";

      for(let i = 0 ; i < Math.min(names.length, 2); i++) {
            initials += names[i][0];
      }

      return initials.toUpperCase();
};

export const addThousandsSeparator = (number) => {
      if(number === null || isNaN(number)) return "";

      const [integerPart, fractionPart] = String(number).split(".");
      const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

      return fractionPart? `${formattedInteger}.${fractionPart}` : formattedInteger;
};

export const prepareExpenseChartData = (data= []) => {
      const chartData =data.map((item) => ({
            category: item.category,
            amount: item.amount,
      }));
 
      return chartData;
}

export const prepareIncomeBarChartData = (data= []) => {
      const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

      const chartData = sortedData.map((item) => ({
            month: moment(item?.date).format("Do MMM"),
            amount: item?.amount,
            source: item?.category,
      })); 
      
      return chartData;
}

export const prepareExpenseBarChartData = (data = []) => {
      const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

      const chartData = sortedData.map((item) => ({
            month: moment(item?.date).format("Do MMM YY"),
            amount: item?.amount,
            category: item?.category,
      })); 
      
      return chartData;
}

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