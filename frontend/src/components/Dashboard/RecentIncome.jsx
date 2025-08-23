import React from 'react';
import { LuArrowRight } from 'react-icons/lu';
import TransactionInfoCard from '../Components Cards/TransactionInfoCard';
import moment from 'moment';

const RecentIncome = ({data, onSeeMore}) => {
      return (
            <div className="card">
                  <div className="flex items-center justify-between">
                        <h5 className="text-lg"> Income </h5>

                        <button onClick={onSeeMore} className="card-btn">
                              See All <LuArrowRight className="text-base" />
                        </button>
                  </div>

                  {data?.slice(0, 5).map((income) => (
                        <TransactionInfoCard
                              key={income._id}
                              title={income.category}
                              icon={income.icon}
                              date={moment(income.date).format('DD MMM YYYY')}
                              amount={income.amount}
                              type="income"
                              hideDeleteBtn
                        />
                  ))}
            </div>
      )
}

export default RecentIncome;
