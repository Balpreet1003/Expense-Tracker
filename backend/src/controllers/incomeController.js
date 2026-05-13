const path = require('path'); 
const xlsx = require('xlsx');
const fs = require('fs');
const Transaction = require('../models/Transaction');

// Download Excel for Income (from Transaction collection)
exports.downloadIncomeExcel = async (req, res) => {
    const userId = req.user.id;
    try {
        // Fetch only income transactions for this user
        const income = await Transaction.find({ 
            userId, 
            type: { $regex: /^income$/i } // case-insensitive match
        }).sort({ date: -1 });

        // Prepare data for excel
        const data = income.map((item) => ({
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
        xlsx.utils.book_append_sheet(wb, ws, "Income");

        // Ensure the downloads directory exists
        const fileName = `income_details_${Date.now()}.xlsx`;
        const filePath = path.join('/tmp', fileName); // Use /tmp for serverless
        xlsx.writeFile(wb, filePath);

        // Send file as response
        res.download(filePath, (err) => {
            fs.unlink(filePath, () => {});
            if (err) {
                res.status(500).json({ message: "Error downloading file" });
            }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Server Error" });
    }
};