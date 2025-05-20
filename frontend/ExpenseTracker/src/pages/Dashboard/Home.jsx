import React from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useUserAuth } from '../../hooks/useUserAuth';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { API_PATHS } from '../../utils/apiPaths';
import axiosInstance from '../../utils/axiosInstance';
import { useEffect } from 'react';
import InfoCard from '../../components/Cards/InfoCard';
import { IoCard } from 'react-icons/io5';
import { LuHandCoins, LuWalletMinimal } from 'react-icons/lu';
import { addThousandsSeparator } from '../../utils/helper';
import RecentTransactions from '../../components/Dashboard/RecentTransactions';
import FinanceOverview from '../../components/Dashboard/FinanceOverview';
import ExpenseTransactions from '../../components/Dashboard/ExpenseTransactions';
import Last30DaysExpenses from '../../components/Dashboard/Last30DaysExpenses';
import RecentIncomeWithCharts from '../../components/Dashboard/RecentIncomeWithCharts';
import RecentIncome from '../../components/Dashboard/RecentIncome';

const Home = () => {
    useUserAuth();

    const navigate = useNavigate();

    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const fetchDashboardData = async () => {
        if(loading) return;

        setLoading(true);

        try {
            const response = await axiosInstance.get(API_PATHS.DASHBOARD.GET_DASHBOARD_DATA);
            if(response.data) setDashboardData(response.data);
        } 
        catch (error) {
            console.error("Failed to fetch dashboard data: ", error);
        } 
        finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchDashboardData();
        return () => {}
    }, []);

    return (
      <DashboardLayout activeMenu='Dashboard'>
        <div className="mx-auto my-5">
          {dashboardData && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <InfoCard
                  icon={<IoCard/>}
                  label="Total Balance"
                  value={addThousandsSeparator(dashboardData?.totalBalance || 0)}
                  color="bg-[#875cf5]"
                />
                <InfoCard
                  icon={<LuWalletMinimal/>}
                  label="Total Income"
                  value={addThousandsSeparator(dashboardData?.totalIncome || 0)}
                  color="bg-orange-500"
                />
                <InfoCard
                  icon={<LuHandCoins/>}
                  label="Total Expense"
                  value={addThousandsSeparator(dashboardData?.totalExpense || 0)}
                  color="bg-red-500"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
                <RecentTransactions 
                  transactions={dashboardData?.recentTransactions}
                  onSeeMore={ ()=> navigate('/expense')  }
                />
                <FinanceOverview
                  totalBalance={dashboardData?.totalBalance || 0}
                  totalIncome={dashboardData?.totalIncome || 0}
                  totalExpense={dashboardData?.totalExpense || 0}
                />

                <ExpenseTransactions
                  transactions={dashboardData?.last30DaysExpense?.transactions || []}
                  onSeeMore={ ()=> navigate('/expense')  }
                />

                <Last30DaysExpenses
                  data={dashboardData?.last30DaysExpense?.transactions || []}
                />

                <RecentIncomeWithCharts
                  data={dashboardData?.last60DaysIncome?.transactions.slice(0.4) || []}
                  totalIncome={dashboardData?.totalIncome || 0}
                />

                <RecentIncome
                  data={dashboardData?.last60DaysIncome?.transactions || []}
                  onSeeMore={ ()=> navigate('/income')  }
                />


              </div>
            </>
          )}
        </div>
      </DashboardLayout>
    )
}

export default Home;
