import React, { useEffect } from 'react';
import { prepareIncomeBarChartData } from '../../utils/helper';
import { LuPlus } from 'react-icons/lu';
import CustomBarChart from '../Charts/CustomBarChart';

const IncomeOverview = ({ transactions, onAddIncome }) => {
      const [chartData, setChartData] = React.useState([]);

      // Group and sum income by date
      const groupedIncomeData = React.useMemo(() => {
            return Object.values(
                  (transactions || []).reduce((acc, txn) => {
                        // Format date as YYYY-MM-DD for grouping
                        const dateKey = new Date(txn.date).toISOString().split('T')[0];
                        if (!acc[dateKey]) {
                              acc[dateKey] = {
                                    ...txn,
                                    date: dateKey,
                                    amount: Number(txn.amount) || 0,
                              };
                        } else {
                              acc[dateKey].amount += Number(txn.amount) || 0;
                        }
                        return acc;
                  }, {})
            );
      }, [transactions]);

      useEffect(() => {
            const result = prepareIncomeBarChartData(groupedIncomeData);
            setChartData(result);
            return () => {};
      }, [groupedIncomeData]);

      return (
            <div className="card">
                  <div className="flex items-center justify-between">
                        <div className="">
                              <h5 className="text-lg">Income Overview</h5>
                              <p className="text-xs text-gray-400 mt-0.5">
                                    Track your earning over time and analyze your income trends.
                              </p>
                        </div>
                        <button className="add-btn" onClick={onAddIncome}>
                              <LuPlus className="text-lg"/>
                              Add Income
                        </button>
                  </div>

                  <div className="mt-10">
                        <CustomBarChart data={chartData}/>
                  </div>
            </div>
      );
};

export default IncomeOverview;
