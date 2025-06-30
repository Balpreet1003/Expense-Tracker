import React from 'react'
import CustomPieChart from '../Charts/CustomPieChart'
import { useEffect } from 'react';

const COLORS = [
  "#875cf5",
  "#9469f6",
  "#a077f6",
  "#ac84f7",
  "#b891f7",
  "#c49ef8",
  "#cfabf8",
  "#d9b7f9",
  "#e2c3f9",
  "#e8caf9",
  "#ead0f9",
  "#ecd5f9",
  "#eedaf9",
  "#f0defa",
  "#f2e2fa",
  "#f4e6fa",
  "#f6eafa",
  "#f8edf9",
  "#faeff8",
  "#eddaf7"
];

const RecentIncomeWithCharts = ({data, totalIncome}) => {

      const [chartData, setChartData] = React.useState([]);

      const prepareChartData = () => {
            const dataArr = data?.map((item) => ({
                  name: item?.category,
                  amount: item?.amount,
            }));

            setChartData(dataArr);
      }

      useEffect(() => {
            prepareChartData();
            return () => {}
      }, [data]);

      return (
            <div className="card">
                  <div className="flex items-center justify-center">
                        <h5 className="text-lg">
                              Last 60 Days Income
                        </h5>
                  </div>

                  <CustomPieChart 
                      data={chartData}
                      label="Total Income"
                      totalAmount={`₹${totalIncome}`}
                      colors={COLORS}
                      showTextAnchor
                  />
            </div>
      )
}

export default RecentIncomeWithCharts
