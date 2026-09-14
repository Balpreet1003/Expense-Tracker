import React, { useEffect } from 'react';
import DashboardLayout from '../../../components/layout/DashboardLayout';
import TransactionsOverview from './View/TransactionsOverview';
import TransactionsList from './View/TransactionsList';
import Modal from '../../../components/Modal';
import AddTransactionsForm from './View/AddTransactionsForm';
import DeleteAlert from '../../../components/DeleteAlert';
import { useUserAuth } from '../../../hooks/useUserAuth';
import { API_PATHS } from '../../../utils/apiPaths'; 
import { toast } from 'react-hot-toast';
import axiosInstance from '../../../utils/axiosInstance';

const Transactions = () => {

      useUserAuth();

      const [OpenAddTransactionMode, setOpenAddTransactionsMode] = React.useState(false);
      const [transactionData, setTransactionData] = React.useState([]);
      const [isLoading, setIsLoading] = React.useState(false);
      const [openDeleteAlert, setOpenDeleteAlert] = React.useState({
            show: false,
            data: null,
            type: null
      });

      //get all transactions details
      const fetchTransactionDetails = async () => {
            if(isLoading) return;

            setIsLoading(true);

            try {
                  const response = await axiosInstance.get(API_PATHS.TRANSACTIONS.GET_ALL);

                  if(response.data) setTransactionData(response.data);
            }
            catch (error) {
                  console.error("Somthing went wrong. Please try again ", error);
            }
            finally {
                  setIsLoading(false);
            }
      };

      // Handle Add transactions
      const handelAddTransactions = async (transaction) => {
            const {
                  userId,
                  icon,
                  type,
                  category,
                  source,
                  amount,
                  date,
                  cards,
                  description,
            } = transaction;

            const transactionType = type?.toLowerCase();

            // Validate amount
            if (!amount || isNaN(amount) || Number(amount) <= 0) {
                  toast.error("Amount should be valid number greater than 0.");
                  return;
            }

            // Validate date
            if (!date) {
                  toast.error("Date is required");
                  return;
            }

            // Validate transaction type
            if (!transactionType) {
                  toast.error("Transaction type is required");
                  return;
            }

            // Validate category for expense
            if ( transactionType === "expense" && !category?.trim()) {
                  toast.error("Category is required");
                  return;
            }

            // Validate source for income
            if ( transactionType === "income" && !source?.trim() ) {
                  toast.error("Source is required");
                  return;
            }

            // Prepare request data
            const requestData = {
                  userId,
                  icon,
                  type: transactionType,
                  amount: Number(amount),
                  date: new Date(date),
                  description,
            };

            // Add category for expense
            if (transactionType === "expense") {
                  requestData.category = category.trim();
            }

            // Add source for income
            if (transactionType === "income") {
                  requestData.source = source.trim();
            }

            try {
                  await axiosInstance.post(
                        API_PATHS.TRANSACTIONS.CREATE,
                        requestData
                  );

                  setOpenAddTransactionsMode(false);

                  toast.success("Transaction added successfully");

                  fetchTransactionDetails();
            } catch (error) {
                  console.error(
                        "Failed to add transaction:",
                        error.response?.data?.message ||
                        error.response?.data?.detail ||
                        error.message
                  );
            }
      };

      // Handel Delete Transaction
      const deleteTransaction = async (TransactionType, TransactionId) => {
            try {
                  await axiosInstance.delete(API_PATHS.TRANSACTIONS.DELETE(TransactionType, TransactionId));
                  setOpenDeleteAlert({ show: false, data: null, type: null });
                  toast.success("Transaction deleted successfully");
                  fetchTransactionDetails();
            }
            catch (error) {
                  console.error("Failed to delete transaction: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // handle download transaction details
      const handleDownloadTransactionDetails = async () => {
            try {
                  const response = await axiosInstance.get(API_PATHS.TRANSACTIONS.DOWNLOAD, { responseType: 'blob' });

                  //create a url fot the blob
                  const url = window.URL.createObjectURL(new Blob([response.data]));
                  const link = document.createElement("a");
                  link.href = url;
                  link.setAttribute("download", "transaction_details.xlsx");
                  document.body.appendChild(link);
                  link.click();
                  link.parentNode.removeChild(link);
                  toast.success("Transaction details downloaded successfully");
                  window.URL.revokeObjectURL(url);
            }
            catch (error) {
                  console.error("Failed to download transaction details: ", error);
                  toast.error("Failed to download transaction details. Please try again.");
            }
      };

      useEffect(() => {
            fetchTransactionDetails();
            return () => {};
      },[]);

      return (
            <DashboardLayout activeMenu='Transactions'>
                   <div className="mx-auto my-5">
                        <div className="grid grid-cols-1 gap-6">
                              <div className="">
                                    <TransactionsOverview
                                          transactions={transactionData}
                                          onAddTransaction={() => setOpenAddTransactionsMode(true)}
                                    />
                              </div>
                        </div>

                        <TransactionsList
                              transactions={transactionData}
                              onDeleteTransaction={(type, id) => {
                                    setOpenDeleteAlert({ show: true, data: id, type: transactionData.find(t => t.id === id)?.type });
                              }}
                              onDownload = {handleDownloadTransactionDetails}
                        />

                        <Modal
                              isOpen={OpenAddTransactionMode}
                              onClose={() => setOpenAddTransactionsMode(false)}
                              title="Add Transaction"
                        >
                              <AddTransactionsForm onAddTransaction={handelAddTransactions}/>
                        </Modal>

                        <Modal
                              isOpen={openDeleteAlert.show}
                              onClose={() => setOpenDeleteAlert({ show: false, data: null, type: null })}
                              title="Delete Transaction"
                        >
                              <DeleteAlert
                                    content="Are you sure you want to delete this transaction?"
                                    onDelete={() => deleteTransaction(openDeleteAlert.type, openDeleteAlert.data)}
                              />
                        </Modal>
                  </div>
            </DashboardLayout>
      )
}

export default Transactions;
