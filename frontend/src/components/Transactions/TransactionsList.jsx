import React from 'react'
import TransactionInfoCard from '../Components Cards/TransactionInfoCard'
import { LuDownload } from 'react-icons/lu'
import moment from 'moment'

const TransactionsList = ({ transactions, onDeleteTransaction, onDownload }) => {
      return (
            <div className="card mt-5">
                  <div className="flex items-center justify-between">
                        <h5 className="text-lg">
                              All Transactions
                        </h5>
                        <button className="card-btn" onClick={onDownload}>
                              <LuDownload className="text-base" /> Download
                        </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2">
                        {transactions.map((transaction) => (
                              <TransactionInfoCard 
                                    key={transaction._id}
                                    title={transaction.category}
                                    icon={transaction.icon}
                                    date={moment(transaction.date).format('DD MMM YYYY')}
                                    amount={transaction.amount}
                                    type={transaction.type} // <-- this is correct
                                    onDelete={() => onDeleteTransaction(transaction._id)}
                              />
                        ))}
                  </div>
            </div>
      )
}

export default TransactionsList
