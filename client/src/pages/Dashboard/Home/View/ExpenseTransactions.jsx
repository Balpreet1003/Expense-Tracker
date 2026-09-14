import moment from 'moment'
import React from 'react'
import { LuArrowRight } from 'react-icons/lu'
import TransactionInfoCard from '../../../../components/Components_Cards/TransactionInfoCard'

const ExpenseTransactions = ({transactions, onSeeMore}) => {
      return (
            <div className="card">
                  <div className="flex items-center justify-between">
                        <h5 className="text-lg">
                              Expenses
                        </h5>
                        <button onClick={onSeeMore} className="card-btn">
                              See All <LuArrowRight className="text-base" />
                        </button>
                  </div>

                  <div className="mt-6">
                        {transactions?.map((expense, index) => (
                              <TransactionInfoCard 
                                key={index}
                                title={expense.category}
                                icon={expense.icon}
                                date={moment(expense.date).format('DD MMM YYYY')}
                                amount={expense.total_amount}
                                type="expense"
                                hideDeleteBtn
                              />
                        ))}
                  </div>
            </div>
      )
}

export default ExpenseTransactions;
