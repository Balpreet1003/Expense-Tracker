const path = require('path'); 
const xlsx = require('xlsx');
const Transaction = require('../models/Transaction'); // Make sure this path is correct

// Download Excel (from Transaction API)
exports.downloadExpenseExcel = async (req, res) => {
      const userId = req.user.id;
      
      try {
            // Fetch only expense transactions for the user
            const expenses = await Transaction.find({
                  userId,
                  type: { $regex: /^expense$/i }
            }).sort({ date: -1 });

            // Prepare data for excel
            const data = expenses.map((item) => ({
                  category: item.category,
                  amount: item.amount,
                  date: item.date,
                  icon: item.icon,
                  cards: item.cards,
                  description: item.description,
            }));

            // Create excel file
            const wb = xlsx.utils.book_new();
            const ws = xlsx.utils.json_to_sheet(data);
            xlsx.utils.book_append_sheet(wb, ws, "Expense");
            const filePath = path.join('/tmp', 'expense_details.xlsx');
            xlsx.writeFile(wb, filePath);
            res.download(filePath);
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      } 
}