import React from 'react';
import TransactionInfoCard from "../Components Cards/TransactionInfoCard";
import { LuDownload } from 'react-icons/lu';
import moment from 'moment';


const ExpenseList = ({ transactions, onDeleteExpense, onDownload }) => {
      return (
            <div className="card mt-5">
                  <div className="flex items-center justify-between">
                        <h5 className="text-lg">
                              Expense Category
                        </h5>
                        <button className="card-btn" onClick={onDownload}>
                              <LuDownload className="text-base" /> Download
                        </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2">
                        {transactions.map((expense) => (
                              <TransactionInfoCard
                                    key={expense._id}
                                    title={expense.category}
                                    icon={expense.icon}
                                    date={moment(expense.date).format('DD MMM YYYY')}
                                    amount={expense.amount}
                                    type="expense"
                                    onDelete={() => onDeleteExpense (expense._id)}
                              />
                        ))}
                  </div>
            </div>
      )
}

export default ExpenseList
