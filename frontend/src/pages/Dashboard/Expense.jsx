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

      //get all expense details
      const fetchExpenseDetails = async () => {
            if (isLoading) return;

            setIsLoading(true);

            try {
                  // Fetch all transactions
                  const response = await axiosInstance.get(API_PATHS.TRANSACTIONS.GET_ALL_TRANSACTIONS);

                  // Filter only expense transactions
                  if (response.data) {
                        const expenseOnly = response.data.filter(
                              txn => txn.type && txn.type.toLowerCase() === "expense"
                        );
                        setExpenseData(expenseOnly);
                  }
            }
            catch (error) {
                  console.error("Something went wrong. Please try again ", error);
            }
            finally {
                  setIsLoading(false);
            }
      };

      // Handel Add Expense
      const handelAddExpense = async (expense) => {
            const {userId, icon, type, category, amount, date, cards, description} = expense;

            if (!category.trim()) {
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
            
            if(!type){
                  toast.error("Transaction type is required");
                  return;
            }

            if(!cards){
                  toast.error("Card is required");
                  return;
            }

            try {
                  await axiosInstance.post(API_PATHS.TRANSACTIONS.ADD_TRANSACTION, {
                        userId,
                        icon,
                        type,
                        category,
                        amount,
                        date: new Date(date),
                        cards,
                        description
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
                  await axiosInstance.delete(API_PATHS.TRANSACTIONS.DELETE_TRANSACTION(expenseId));
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

      // handle download expense details
      const handleDownloadExpenseDetails = async () => {
            try {
                  const response = await axiosInstance.get(API_PATHS.EXPENSE.DOWNLOAD_EXPENSE, {
                        responseType: 'blob'
                  });

                  // Try to get filename from response headers, fallback to default
                  const disposition = response.headers['content-disposition'];
                  let filename = "expense_details.xlsx";
                  if (disposition && disposition.indexOf('filename=') !== -1) {
                        filename = disposition.split('filename=')[1].replace(/"/g, '');
                  }

                  const url = window.URL.createObjectURL(new Blob([response.data]));
                  const link = document.createElement("a");
                  link.href = url;
                  link.setAttribute("download", filename);
                  document.body.appendChild(link);
                  link.click();
                  link.parentNode.removeChild(link);
                  window.URL.revokeObjectURL(url);
                  toast.success("Expense details downloaded successfully");
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
