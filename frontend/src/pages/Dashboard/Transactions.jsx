import React, { useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import TransactionsOverview from '../../components/Transactions/TransactionsOverview';
import TransactionsList from '../../components/Transactions/TransactionsList';
import Modal from '../../components/Modal';
import AddTransactionsForm from '../../components/Transactions/AddTransactionsForm';
import DeleteAlert from '../../components/DeleteAlert';
import { useUserAuth } from '../../hooks/useUserAuth';
import { API_PATHS } from '../../utils/apiPaths';
import { toast } from 'react-hot-toast';
import axiosInstance from '../../utils/axiosInstance';

const Transactions = () => {

      useUserAuth();

      const [OpenAddTransactionMode, setOpenAddTransactionsMode] = React.useState(false);
      const [transactionData, setTransactionData] = React.useState([]);
      const [isLoading, setIsLoading] = React.useState(false);
      const [openDeleteAlert, setOpenDeleteAlert] = React.useState({
            show: false,
            data: null,
      });

      //get all transactions details
      const fetchTransactionDetails = async () => {
            if(isLoading) return;

            setIsLoading(true);

            try {
                  const response = await axiosInstance.get(API_PATHS.TRANSACTIONS.GET_ALL_TRANSACTIONS);

                  if(response.data) setTransactionData(response.data);
            }
            catch (error) {
                  console.error("Somthing went wrong. Please try again ", error);
            }
            finally {
                  setIsLoading(false);
            }
      };

      // Handel Add transactions
      const handelAddTransactions = async (transaction) => {
            const {userId, icon, type, category, amount, date, cards, description} = transaction;

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

                  setOpenAddTransactionsMode(false);
                  toast.success("Transaction added successfully");
                  fetchTransactionDetails();
            }
            catch (error) {
                  console.error("Failed to add transaction: ", 
                        error.response?.data?.message || error.message
                  );
            }
      };

      // Handel Delete Transaction
      const deleteTransaction = async (TransactionId) => {
            try {
                  await axiosInstance.delete(API_PATHS.TRANSACTIONS.DELETE_TRANSACTION(TransactionId));
                  setOpenDeleteAlert({ show: false, data: null });
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
                  const response = await axiosInstance.get(API_PATHS.TRANSACTIONS.DOWNLOAD_TRANSACTIONS, { responseType: 'blob' });

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
                              onDeleteTransaction={(id) => {
                                    setOpenDeleteAlert({ show: true, data: id })
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
                              onClose={() => setOpenDeleteAlert({ show: false, data: null })}
                              title="Delete Transaction"
                        >
                              <DeleteAlert
                                    content="Are you sure you want to delete this transaction?"
                                    onDelete={() => deleteTransaction(openDeleteAlert.data)}
                              />
                        </Modal>
                  </div>
            </DashboardLayout>
      )
}

export default Transactions;
