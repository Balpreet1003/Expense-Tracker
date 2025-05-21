import React from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import IncomeOverview from '../../components/Income/IncomeOverview'
import { API_PATHS } from '../../utils/apiPaths';
import axiosInstance from '../../utils/axiosInstance';
import { useEffect } from 'react';
import Modal from '../../components/Modal';
import AddIncomeForm from '../../components/Income/AddIncomeForm';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Income = () => {

      const [OpenAddIncomeMode, setOpenAddIncomeMode] = React.useState(false);
      const [incomeData, setIncomeData] = React.useState([]);
      const [isLoading, setIsLoading] = React.useState(false);
      const [openDeleteAlert, setOpenDeleteAlert] = React.useState({
            show: false,
            data: null,
      });

      //get all income details
      const fetchIncomeDetails = async () => {
            if(isLoading) return;

            setIsLoading(true);

            try {
                  const response = await axiosInstance.get(API_PATHS.INCOME.GET_ALL_INCOME);

                  if(response.data) setIncomeData(response.data);
            }
            catch (error) {
                  console.error("Somthing went wrong. Please try again ", error);
            }
            finally {
                  setIsLoading(false);
            }
      };

      // Handel Add Income
      const handelAddIncome = async (income) => {
            if (!income || typeof income.source !== "string") {
                  toast.error("Source is required");
                  eturn;
            }
            const {source, amount, date, icon} = income;

            if (!source.trim()) {
                  toast.error("Source is required");
                  return;
            }

            if(!amount || isNaN(amount) || Number(amount) <= 0){
                  toast.error("Amount should be valid number greater than 0.")
            }

            if(!date){
                  toast.error("Date is required");
                  return;
            }

            try {
                  await axiosInstance.post(API_PATHS.INCOME.ADD_INCOME, {source, amount, date, icon});

                  setOpenAddIncomeMode(false);
                  toast.success("Income added successfully");
                  fetchIncomeDetails();
            }
            catch (error) {
                  console.error("Failed to add income: ", 
                        error.response?.data?.message ||error.message
                  );
            }
      };

      // Handel Delete Income
      const deleteIncome = async (incomeId) => {};

      // handle download income details
      const handleDownloadIncomeDetails = async () => {};

      useEffect(() => {
            fetchIncomeDetails();
            return () => {};
      },[]);

      return (
            <DashboardLayout activeMenu='Income'>
                  <div className="mx-auto my-5">
                        <div className="grid grid-cols-1 gap-6">
                              <div className="">
                                    <IncomeOverview 
                                          transactions={incomeData}
                                          onAddIncome={() => setOpenAddIncomeMode(true)}
                                    />
                              </div>
                        </div>

                        <Modal
                              isOpen={OpenAddIncomeMode}
                              onClose={() => setOpenAddIncomeMode(false)}
                              title="Add Income"
                        >
                              <AddIncomeForm onAddIncome={handelAddIncome}/>
                        </Modal>
                  </div>
            </DashboardLayout>
      )
}

export default Income
