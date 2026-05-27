const path = require('path'); 
const xlsx = require('xlsx');
const fs = require('fs');
const { pool, query, refreshAnalyticsMaterializedViews } = require('../config/db');
const { invalidateUserAnalyticsCache } = require('../services/financialAnalyticsService');
const {
      parseIntegerId,
      parsePositiveAmount,
      toTransactionResponse,
      toTransactionExcelRow,
} = require('../utils/pgHelpers');

const normalizeTransactionType = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().toLowerCase();
};

const parseTransactionDate = (value) => {
      if (typeof value !== 'string' && !(value instanceof Date)) {
            return null;
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return null;
      }

      return date;
};

// add transaction
exports.addTransaction = async (req, res) => {
      const userId = req.user.id;

      try {
            const icon = typeof req.body.icon === 'string' ? req.body.icon.trim() : '';
            const type = normalizeTransactionType(req.body.type);
            const category = typeof req.body.category === 'string' ? req.body.category.trim() : '';
            const amount = parsePositiveAmount(req.body.amount);
            const date = parseTransactionDate(req.body.date);
            const description = typeof req.body.description === 'string' ? req.body.description.trim() : '';
            const cardId = parseIntegerId(req.body.cardId ?? req.body.card_id);
            const cards = typeof req.body.cards === 'string' ? req.body.cards.trim() : '';

            // validation: check for missing fields
            if (!type || !category || amount === null || !date) {
                  return res.status(400).json({ message: "All fields are required" });
            }

            if (!['income', 'expense'].includes(type)) {
                  return res.status(400).json({ message: "Transaction type must be income or expense" });
            }

            let resolvedCardName = cards;
            let resolvedCardId = null;

            if (cardId) {
                  const cardResult = await query(
                        `SELECT id, card_name
                         FROM cards
                         WHERE id = $1 AND user_id = $2
                         LIMIT 1`,
                        [cardId, userId]
                  );

                  if (!cardResult.rowCount) {
                        return res.status(404).json({ message: "Card not found" });
                  }

                  resolvedCardId = cardResult.rows[0].id;

                  if (!resolvedCardName) {
                        resolvedCardName = cardResult.rows[0].card_name;
                  }
            }
 
            const result = await query(
                  `INSERT INTO transactions (user_id, card_id, cards, icon, type, category, amount, date, description)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                   RETURNING id, user_id, card_id, cards, icon, type, category, amount, date, description, created_at, updated_at`,
                  [userId, resolvedCardId, resolvedCardName, icon, type, category, amount, date, description]
            );

            await refreshAnalyticsMaterializedViews();
            await invalidateUserAnalyticsCache(userId);

            res.status(201).json(toTransactionResponse(result.rows[0]));
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}

// get all transactions
exports.getAllTransaction = async (req, res) => {
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
                          t.created_at,
                          t.updated_at,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                   ORDER BY t.date DESC, t.id DESC`,
                  [userId]
            );

            res.json(result.rows.map(toTransactionResponse));
      } 
      catch (error) {
            res.status(500).json({ message: "Server Error" });
      }
}

//delete transaction
exports.deleteTransaction = async (req, res) => {
      try {
            const transactionId = parseIntegerId(req.params.id);

            if (!transactionId) {
                  return res.status(400).json({ message: "Invalid transaction id" });
            }

            const result = await query(
                  `DELETE FROM transactions
                   WHERE id = $1 AND user_id = $2
                   RETURNING id`,
                  [transactionId, req.user.id]
            );

            if (!result.rowCount) {
                  return res.status(404).json({ message: "Transaction not found" });
            }

            await refreshAnalyticsMaterializedViews();
            await invalidateUserAnalyticsCache(req.user.id);

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
                   ORDER BY t.date DESC, t.id DESC`,
                  [userId]
            );

            // prepare data for excel
            const data = result.rows.map(toTransactionExcelRow);

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