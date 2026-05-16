const path = require('path'); 
const xlsx = require('xlsx');
const fs = require('fs');
const { query } = require('../config/db');
const { toTransactionExcelRow } = require('../utils/pgHelpers'); // Make sure this path is correct

// Download Excel (from Transaction API)
exports.downloadExpenseExcel = async (req, res) => {
      const userId = req.user.id;
      
      try {
            const result = await query(
                  `SELECT t.id,
                          t.user_id,
                          t.card_id,
                          t.cards,
                          t.icon,
                          t.type,
                          t.category,
                          t.amount,
                          t.date,
                          t.description,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                                                             AND LOWER(t.type::text) = 'expense'
                   ORDER BY t.date DESC, t.id DESC`,
                  [userId]
            );

            // Prepare data for excel
            const data = result.rows.map(toTransactionExcelRow);

            // Create excel file
            const wb = xlsx.utils.book_new();
            const ws = xlsx.utils.json_to_sheet(data);
            xlsx.utils.book_append_sheet(wb, ws, "Expense");
            const filePath = path.join('/tmp', `expense_details_${Date.now()}.xlsx`);
            xlsx.writeFile(wb, filePath);

            res.download(filePath, (err) => {
                  fs.unlink(filePath, () => {});
                  if (err) {
                        res.status(500).json({ message: "Error downloading file" });
                  }
            });
      }
      catch (error) {
            res.status(500).json({message: "Server Error"});
      } 
}