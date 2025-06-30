import React, { useEffect } from 'react'
import { LuPlus } from 'react-icons/lu';
import { prepareTransactionLineChartData } from '../../utils/helper';
import CustomTransactionLineChart from '../Charts/CustomTransactionLineChart';

const TransactionsOverview = ({ transactions, onAddTransaction}) => {

      const [incomeData, setIncomeData] = React.useState([]);
      const [expenseData, setExpenseData] = React.useState([]);

      // Group and sum transactions by date and type
      const groupedTransactions = React.useMemo(() => {
            const grouped = {};
            (transactions || []).forEach(txn => {
                  const dateKey = new Date(txn.date).toISOString().split('T')[0];
                  const type = txn.type || 'unknown';
                  const key = `${dateKey}_${type}`;
                  if (!grouped[key]) {
                        grouped[key] = {
                              ...txn,
                              date: dateKey,
                              amount: Number(txn.amount) || 0,
                        };
                  } else {
                        grouped[key].amount += Number(txn.amount) || 0;
                  }
            });
            return Object.values(grouped);
      }, [transactions]);
      
      useEffect(()=> {
            const { incomeData, expenseData } = prepareTransactionLineChartData(groupedTransactions);
            setIncomeData(incomeData);
            setExpenseData(expenseData);

            return () => {};
      }, [groupedTransactions]);

      return (
            <div className="card">
                  <div className="flex items-center justify-between">
                        <div className="">
                              <h5 className="text-lg">Transaction Overview</h5>
                              <p className="text-xs text-gray-400 mt-0.5">
                                    Track your earning over time and analyze your transaction trands.
                              </p>
                        </div>
                        <button className="add-btn" onClick={onAddTransaction}>
                              <LuPlus className="text-lg"/>
                              Add Transaction
                        </button>
                  </div> 

                  <div className="mt-10">
                        <CustomTransactionLineChart trxIncome={incomeData} trxExpense={expenseData}/>
                  </div>

            </div>
      )
}

export default TransactionsOverview
