// import React from 'react'
// import { useUserAuth } from '../../hooks/useUserAuth';
// import DashboardLayout from '../../components/layout/DashboardLayout';
// import { API_PATHS } from '../../utils/apiPaths';
// import axiosInstance from '../../utils/axiosInstance';

// const Expense = () => {

//       useUserAuth();
      
//       const [OpenAddExpenseMode, setOpenAddExpenseMode] = React.useState(false);
//       const [expenseData, setExpenseData] = React.useState([]);
//       const [isLoading, setIsLoading] = React.useState(false);
//       const [openDeleteAlert, setOpenDeleteAlert] = React.useState({
//             show: false,
//             data: null,
//       });

//       //get all income details
//       const fetchExpenseDetails = async () => {
//             if(isLoading) return;

//             setIsLoading(true);

//             try {
//                   const response = await axiosInstance.get(API_PATHS.EXPENSE.GET_ALL_EXPENSE);

//                   if(response.data) setExpenseData(response.data);
//             }
//             catch (error) {
//                   console.error("Somthing went wrong. Please try again ", error);
//             }
//             finally {
//                   setIsLoading(false);
//             }
//       };

//       // Handel Add Income
//       const handelAddExpense = async (expense) => {
//             const {category, amount, date, icon} = expense;

//             if (!category.trim()) {
//                   toast.error("Category is required");
//                   return;
//             }

//             if(!amount || isNaN(amount) || Number(amount) <= 0){
//                   toast.error("Amount should be valid number greater than 0.");
//                   return;
//             }

//             if(!date){
//                   toast.error("Date is required");
//                   return;
//             }

//             try {
//                   await axiosInstance.post(API_PATHS.EXPENSE.ADD_EXPENSE, {
//                         category,
//                         amount,
//                         date,
//                         icon,
//                   });

//                   setOpenAddExpenseMode(false);
//                   toast.success("Expense added successfully");
//                   fetchExpenseDetails();
//             }
//             catch (error) {
//                   console.error("Failed to add expense: ", 
//                         error.response?.data?.message || error.message
//                   );
//             }
//       };

//       return (
//             <DashboardLayout activeMenu='Expense'>
//                   <div className="mx-auto my-5">

//                   </div>
//             </DashboardLayout>
//       )
// }

// export default Expense


import React from 'react'

const Expense = () => {
      return (
            <div>
                  Expense
            </div>
      )
}

export default Expense
