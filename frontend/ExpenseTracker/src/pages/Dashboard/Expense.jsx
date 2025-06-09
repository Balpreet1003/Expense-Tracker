import React from 'react'
import { useUserAuth } from '../../hooks/useUserAuth';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { API_PATHS } from '../../utils/apiPaths';
import axiosInstance from '../../utils/axiosInstance';
import { useEffect } from 'react';
import ExpenseOverview from '../../components/Expense/ExpenseOverview';
import AddExpenseForm from '../../components/Expense/AddExpenseForm';
import Modal from '../../components/Modal';
import { toast } from'react-hot-toast';
import DeleteAlert from '../../components/DeleteAlert';
import ExpenseList from '../../components/Expense/ExpenseList';

const Expense = () => {

      useUserAuth();
      
      const [OpenAddExpenseMode, setOpenAddExpenseMode] = React.useState(false);
      const [expenseData, setExpenseData] = React.useState([]);
      const [isLoading, setIsLoading] = React.useState(false);
      const [openDeleteAlert, setOpenDeleteAlert] = React.useState({
            show: false,
            data: null,
      });

      //get all income details
      const fetchExpenseDetails = async () => {
            if(isLoading) return;

            setIsLoading(true);

            try {
                  const response = await axiosInstance.get(API_PATHS.EXPENSE.GET_ALL_EXPENSE);

                  if(response.data) setExpenseData(response.data);
            }
            catch (error) {
                  console.error("Somthing went wrong. Please try again ", error);
            }
            finally {
                  setIsLoading(false);
            }
      };

      // Handel Add Income
      const handelAddExpense = async (expense) => {
            const {category, amount, date, icon} = expense;

            if (!category.trim()) {
                  toast.error("Category is required");
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
                  await axiosInstance.post(API_PATHS.EXPENSE.ADD_EXPENSE, {
                        category,
                        amount,
                        date,
                        icon,
                  });

                  setOpenAddExpenseMode(false);
                  toast.success("Expense added successfully");
                  fetchExpenseDetails();
            }
            catch (error) {
                  console.error("Failed to add expense: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // Handel Delete Expense
      const deleteExpense = async (expenseId) => {
            try {
                  await axiosInstance.delete(API_PATHS.EXPENSE.DELETE_EXPENSE(expenseId));
                  setOpenDeleteAlert({ show: false, data: null });
                  toast.success("Expense deleted successfully");
                  fetchExpenseDetails();
            }
            catch (error) {
                  console.error("Failed to delete expense: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // handle download income details
      const handleDownloadExpenseDetails = async () => {
            try {
                  const response = await axiosInstance.get(API_PATHS.EXPENSE.DOWNLOAD_EXPENSE, { responseType: 'blob' });

                  //create a url fot the blob
                  const url = window.URL.createObjectURL(new Blob([response.data]));
                  const link = document.createElement("a");
                  link.href = url;
                  link.setAttribute("download", "expense_details.xlsx");
                  document.body.appendChild(link);
                  link.click();
                  link.parentNode.removeChild(link);
                  toast.success("Expense details downloaded successfully");
                  window.URL.revokeObjectURL(url);
            }
            catch (error) {
                  console.error("Failed to download expense details: ", error);
                  toast.error("Failed to download expense details. Please try again.");
            }
      }; 

      useEffect(() => {
            fetchExpenseDetails();
            return () => {};
      },[]);

      return (
            <DashboardLayout activeMenu='Expense'>
                  <div className="mx-auto my-5">
                        <div className="grid grid-cols-1 gap-6">
                              <div className="">
                                    <ExpenseOverview 
                                          transactions={expenseData}
                                          onAddExpense={() => setOpenAddExpenseMode(true)}
                                    />
                              </div>
                        </div>

                        <ExpenseList
                              transactions={expenseData}
                              onDeleteExpense={(expenseId) => {
                                    setOpenDeleteAlert({
                                             show: true,
                                             data: expenseId,
                                        });
                              }}
                              onDownload = {handleDownloadExpenseDetails}
                        />

                        <Modal 
                              isOpen={OpenAddExpenseMode}
                              onClose={() => setOpenAddExpenseMode(false)}
                              title="Add Expense"
                        >
                              <AddExpenseForm onAddExpense={handelAddExpense}/>
                        </Modal>

                        <Modal
                              isOpen={openDeleteAlert.show}
                              onClose={() => setOpenDeleteAlert({ show: false, data: null })}
                              title="Delete Exepnse"
                        >
                              <DeleteAlert
                                    content="Are you sure you want to delete this expense?"
                                    onDelete={() => deleteExpense(openDeleteAlert.data)}
                              />
                        </Modal>
                  </div>
            </DashboardLayout>
      )
}

export default Expense
