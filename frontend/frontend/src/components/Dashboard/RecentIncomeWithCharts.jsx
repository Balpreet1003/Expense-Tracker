import React from 'react'
import CustomPieChart from '../Charts/CustomPieChart'
import { useEffect } from 'react';

const COLORS = ["#875CF5", "#FA2C37", "#FF6900", "4F39F6"];

const RecentIncomeWithCharts = ({data, totalIncome}) => {

      const [chartData, setChartData] = React.useState([]);

      const prepareChartData = () => {
            const dataArr = data?.map((item) => ({
                  name: item?.source,
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
