const mongoose = require("mongoose");

const CardSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    cardName: { type: String, required: true },
    cardNumber: { type: String, required: true, unique: true },
    cardType: { type: String, required: true }, // e.g., "Visa", "MasterCard", etc.
    expiryDate: { type: Date, required: true },
    cvv: { type: String, required: true },
    bankName: { type: String, required: true },
    isDefault: { type: Boolean, default: false }, // to mark the default card
}, { timestamps: true });

module.exports = mongoose.model("Cards", CardSchema);