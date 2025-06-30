import React from 'react'
import { AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Area } from "recharts"

// Helper to merge income and expense by date
function mergeIncomeExpense(income = [], expense = []) {
      const map = {};
      income.forEach(item => {
            map[item.date] = { date: item.date, income: item.amount, expense: 0, category: item.category };
      });
      expense.forEach(item => {
            if (map[item.date]) {
                  map[item.date].expense = item.amount;
                  map[item.date].expenseCategory = item.category;
            } else {
                  map[item.date] = { date: item.date, income: 0, expense: item.amount, expenseCategory: item.category };
            }
      });
      // Sort by date
      return Object.values(map).sort((a, b) => new Date(a.date) - new Date(b.date));
}

const CustomTransactionLineChart = ({ trxIncome = [], trxExpense = [] }) => {
      const data = mergeIncomeExpense(trxIncome, trxExpense);

      const CustomTooltip = ({ active, payload }) => {
            if (active && payload && payload.length) {
                  return (
                        <div className="bg-white shadow-md rounded-lg p-2 border border-gray-300">
                              <p className="text-xs font-semibold text-purple-800 mb-1">{payload[0].payload.date}</p>
                              <p className="text-sm ">
                                    Income: <span className="font-medium text-green-700">₹{payload[0].payload.income}</span>
                              </p>
                              <p className="text-sm text-red-700">
                                    Expense: <span className="font-medium">₹{payload[0].payload.expense}</span>
                              </p>
                        </div>
                  )
            }
            return null;
      }

      return (
            <div className="bg-white">
                  <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={data}>
                              <defs>
                                    <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
                                          <stop offset="5%" stopColor="#9972fc" stopOpacity={0.4} />
                                          <stop offset="95%" stopColor="#9972fc" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="expenseGradient" x1="0" y1="0" x2="0" y2="1">
                                          <stop offset="5%" stopColor="#80759c" stopOpacity={0.4} />
                                          <stop offset="95%" stopColor="#80759c" stopOpacity={0} />
                                    </linearGradient>
                              </defs>
                              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#555", stroke: "none" }} />
                              <YAxis tick={{ fontSize: 12, fill: "#555", stroke: "none" }} />
                              <Tooltip content={CustomTooltip} />
                              <Area
                                    type="monotone"
                                    dataKey="income"
                                    stroke="#9972fc"
                                    fill="url(#incomeGradient)"
                                    strokeWidth={3}
                                    dot={{ r: 0, fill: "#9972fc" }}
                                    name="Income"
                              />
                              <Area
                                    type="monotone"
                                    dataKey="expense"
                                    stroke="#80759c"
                                    fill="url(#expenseGradient)"
                                    strokeWidth={3}
                                    dot={{ r: 0, fill: "#80759c" }}
                                    name="Expense"
                              />
                        </AreaChart>
                  </ResponsiveContainer>
            </div>
      )
}

export default CustomTransactionLineChart
