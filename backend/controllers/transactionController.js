const path = require('path'); 
const xlsx = require('xlsx');
const fs = require('fs');
const Transaction = require('../models/Transaction');

// add transaction
exports.addTransaction = async (req, res) => {
      const userId = req.user.id;

      try {
            const { icon, type, category, amount, date, cards, description } = req.body;

            // validation: check for missing fields
            if (!type || !category || !amount || !date || !cards) {
                  return res.status(400).json({ message: "All fields are required" });
            }
 
            const newTransaction = new Transaction({
                  userId,
                  icon,
                  type,
                  category,
                  amount,
                  date: new Date(date),
                  cards,
                  description
            }); 
 
            await newTransaction.save();
            res.status(200).json(newTransaction);
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}

// get all transactions
exports.getAllTransaction = async (req, res) => {
      const userId = req.user.id;

      try {
            const transactions = await Transaction.find({ userId }).sort({ date: -1 });
            res.json(transactions);
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}

// delete transaction
exports.deleteTransaction = async (req, res) => {
      try {
            await Transaction.findByIdAndDelete(req.params.id);
            res.status(200).json({ message: "Transaction Deleted" });
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}

// download transactions as excel
exports.downloadTransactionExcel = async (req, res) => {
      const userId = req.user.id;

      try {
            const transactions = await Transaction.find({ userId }).sort({ date: -1 });

            // prepare data for excel
            const data = transactions.map((item) => ({
                  icon: item.icon,
                  type: item.type,
                  category: item.category,
                  amount: item.amount,
                  date: item.date,
                  cards: item.cards,
                  description: item.description
            }));

            // create a new workbook and add a worksheet
            const workbook = xlsx.utils.book_new();
            const worksheet = xlsx.utils.json_to_sheet(data);

            // append the worksheet to the workbook
            xlsx.utils.book_append_sheet(workbook, worksheet, 'Transactions');

            // generate a file name with timestamp
            const fileName = `transactions_${Date.now()}.xlsx`;
            const filePath = path.join('/tmp', fileName); // Use /tmp for serverless

            // write the workbook to a file
            xlsx.writeFile(workbook, filePath);

            // send the file as a response
            res.download(filePath, (err) => {
                  fs.unlink(filePath, () => {}); // delete the file after sending
                  if (err) {
                        res.status(500).json({ message: "Error downloading file" });
                  }
            });
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}