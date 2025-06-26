const path = require('path'); 
const xlsx = require('xlsx');
const Income = require('../models/Income');

// Add Income Source
exports.addIncome = async (req, res) => {
      const userId = req.user.id;

      try {
            const { icon, source, amount, date}= req.body;

            //validation: check for missing fil=elds
            if(!source || !amount || !date) {
                  return res.status(400).json({message: "All fields are required"});
            }

            const newIncome = new Income({
                  userId,
                  icon,
                  source,
                  amount,
                  date: new Date(date)
            })

            await newIncome.save(); 
            res.status(200).json(newIncome);
      } 
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Get All Income Source
exports.getAllIncome = async (req, res) => {
      const userId = req.user.id;

      try {
            const income = await Income.find({userId}).sort({date: -1});
            res.json(income);
      } 
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Delete Income Source
exports.deleteIncome = async (req, res) => {
      try {
            await Income.findByIdAndDelete(req.params.id);
            res.status(200).json({message: "Income Source Deleted"});
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      }
}


// Download Excel
exports.downloadIncomeExcel = async (req, res) => {
      const userId = req.user.id;
      
      try {
            const income = await Income.find({userId}).sort({date: -1});

            //prepare data for excel
            const data = income.map((item) => ({
                  source: item.source,
                  amount: item.amount,
                  date: item.date,
            }));

            //create excel file
            const wb = xlsx.utils.book_new();
            const ws = xlsx.utils.json_to_sheet(data);
            xlsx.utils.book_append_sheet(wb, ws, "Income");
            const filePath = path.join('/tmp', 'income_details.xlsx');
            xlsx.writeFile(wb, filePath);
            res.download(filePath);
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      } 
}  