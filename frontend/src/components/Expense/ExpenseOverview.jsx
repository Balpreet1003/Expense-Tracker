import React, { useEffect } from 'react'
import { prepareExpenseBarChartData } from '../../utils/helper';
import { LuPlus } from 'react-icons/lu';
import CustomLineChart from '../Charts/CustomLineChart';

const ExpenseOverview = ({ transactions, onAddExpense }) => {
      const [chartData, setChartData] = React.useState([]);

      const groupByDateAndCategory = React.useMemo(() => {
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
            const result = prepareExpenseBarChartData(groupByDateAndCategory);
            setChartData(result);
            return () => {};
      }, [groupByDateAndCategory]);

    return (
        <div className="card">
            <div className="flex items-center justify-between">
                <div className="flex flex-col">
                    <h5 className="text-lg">Expense Overview</h5>
                    <p className="text-xs text-gray-400 mt-0.5">
                        Track your spending trend over time and gain insights into where your money goes.
                    </p>
                </div>
                <button className="add-btn" onClick={onAddExpense}>
                    <LuPlus className="text-lg"/>
                    Add Expense
                </button>
            </div>

            <div className="mt-10">
                <CustomLineChart data={chartData}/>
            </div>
        </div>
    )
}

export default ExpenseOverview;
