const mongoose = require('mongoose');

const expenseSchema = new mongoose.Schema({
    userId: { type: String, required: true },
    icon: String,
    category: { type: String, required: true },
    amount: { type: Number, required: true },
    date: { type: Date, required: true }
});
 
module.exports = mongoose.model('Expense', expenseSchema);