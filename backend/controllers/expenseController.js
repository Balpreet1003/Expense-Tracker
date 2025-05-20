const xlsx = require('xlsx');
const Expense = require('../models/Expense');

// Add Expense Source
exports.addExpense = async (req, res) => {
      const userId = req.user.id;

      try {
            const { icon, category, amount, date}= req.body;

            //validation: check for missing fil=elds
            if(!category || !amount || !date) {
                  return res.status(400).json({message: "All fields are required"});
            }

            const newExpense = new Expense({
                  userId,
                  icon,
                  category,
                  amount,
                  date: new Date(date)
            })

            await newExpense.save(); 
            res.status(200).json(newExpense);
      } 
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Get All Expense Source
exports.getAllExpense = async (req, res) => {
      const userId = req.user.id;

      try {
            const expense = await Expense.find({userId}).sort({date: -1});
            res.json(expense);
      } 
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Delete Expense Source
exports.deleteExpense = async (req, res) => {
      try {
            await Expense.findByIdAndDelete(req.params.id);
            res.status(200).json({message: "Expense Deleted"});
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Download Excel
exports.downloadExpenseExcel = async (req, res) => {
      const userId = req.user.id;
      
      try {
            const expense = await Expense.find({userId}).sort({data: -1});

            //prepare data for excel
            const data = expense.map((item) => ({
                  category: item.category,
                  amount: item.amount,
                  date: item.date,
            }));

            //create excel file
            const wb = xlsx.utils.book_new();
            const ws = xlsx.utils.json_to_sheet(data);
            xlsx.utils.book_append_sheet(wb, ws, "Expense");
            xlsx.writeFile(wb, 'expense_details.xlsx');
            res.download('expense_details.xlsx');
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      } 
} 