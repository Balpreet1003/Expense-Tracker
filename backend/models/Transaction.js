const mongoose = require("mongoose");

const TransactionSchema = new mongoose.Schema({
      userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
      icon: { type: String },
      type: { type: String, required: true }, // "income" or "expense"
      category: { type: String, required: true },
      amount: { type: Number, required: true },
      date: { type: Date, default: Date.now },
      cards: { type: String, default: "" }, // determine transaction form which bank account and card type
      description: { type: String, default: "" },
}, { timestamps: true });

module.exports = mongoose.model("Transaction", TransactionSchema);