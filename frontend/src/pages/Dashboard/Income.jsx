import React from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import IncomeOverview from '../../components/Income/IncomeOverview'
import { API_PATHS } from '../../utils/apiPaths';
import axiosInstance from '../../utils/axiosInstance';
import { useEffect } from 'react';
import Modal from '../../components/Modal';
import AddIncomeForm from '../../components/Income/AddIncomeForm';
import { toast } from 'react-hot-toast';
import IncomeList from '../../components/Income/IncomeList';
import DeleteAlert from '../../components/DeleteAlert';
import { useUserAuth } from '../../hooks/useUserAuth';

const Income = () => {
      useUserAuth();

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
            const {source, amount, date, icon} = income;

            if (!source.trim()) {
                  toast.error("Source is required");
                  return;
            }

            if(!amount || isNaN(amount) || Number(amount) <= 0){
                  toast.error("Amount should be valid number greater than 0.");
                  return;
            }

            if(!date){
                  toast.error("Date is required");
                  return;
            }

            try {
                  await axiosInstance.post(API_PATHS.INCOME.ADD_INCOME, {
                        source,
                        amount,
                        date,
                        icon,
                  });

                  setOpenAddIncomeMode(false);
                  toast.success("Income added successfully");
                  fetchIncomeDetails();
            }
            catch (error) {
                  console.error("Failed to add income: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // Handel Delete Income
      const deleteIncome = async (incomeId) => {
            try {
                  await axiosInstance.delete(API_PATHS.INCOME.DELETE_INCOME(incomeId));
                  setOpenDeleteAlert({ show: false, data: null });
                  toast.success("Income deleted successfully");
                  fetchIncomeDetails();
            }
            catch (error) {
                  console.error("Failed to delete income: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // handle download income details
      const handleDownloadIncomeDetails = async () => {
            try {
                  const response = await axiosInstance.get(API_PATHS.INCOME.DOWNLOAD_INCOME, { responseType: 'blob' });

                  //create a url fot the blob
                  const url = window.URL.createObjectURL(new Blob([response.data]));
                  const link = document.createElement("a");
                  link.href = url;
                  link.setAttribute("download", "income_details.xlsx");
                  document.body.appendChild(link);
                  link.click();
                  link.parentNode.removeChild(link);
                  toast.success("Income details downloaded successfully");
                  window.URL.revokeObjectURL(url);
            }
            catch (error) {
                  console.error("Failed to download income details: ", error);
                  toast.error("Failed to download income details. Please try again.");
            }
      };

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

                        <IncomeList
                              transactions={incomeData}
                              onDeleteIncome={(id) => {
                                    setOpenDeleteAlert({ show: true, data: id })
                              }}
                              onDownload = {handleDownloadIncomeDetails}
                        />

                        <Modal
                              isOpen={OpenAddIncomeMode}
                              onClose={() => setOpenAddIncomeMode(false)}
                              title="Add Income"
                        >
                              <AddIncomeForm onAddIncome={handelAddIncome}/>
                        </Modal>

                        <Modal
                              isOpen={openDeleteAlert.show}
                              onClose={() => setOpenDeleteAlert({ show: false, data: null })}
                              title="Delete Income"
                        >
                              <DeleteAlert
                                    content="Are you sure you want to delete this income?"
                                    onDelete={() => deleteIncome(openDeleteAlert.data)}
                              />
                        </Modal>
                  </div>
            </DashboardLayout>
      )
}

export default Income;