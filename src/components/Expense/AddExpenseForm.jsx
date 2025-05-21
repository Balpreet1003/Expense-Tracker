import React from 'react'
import EmojiPickerPopup from "../EmojiPickerPopup";
import Input from "../Input/Input";

const AddExpenseForm = ({ onAddExpense }) => {

      const [expense, setExpense] = React.useState({
            category: "",
            amount: "",
            date: "",
            icon: "",
      });

      // Handle Form Change
      const handleChange = (key, value) => {
            setExpense({...expense, [key]: value });
      };

      return (
            <div>
                  <EmojiPickerPopup
                      icon={expense.icon}
                      onSelect={(selectIcon) => handleChange("icon", selectIcon)}
                  />

                  <Input
                        value={expense.category}
                        onChange={(e) => handleChange("category", e.target.value)}
                        label="Category"
                        placeholder="e.g. Food, Entertainment, Utilities, etc."
                        type="text"
                  />

                  <Input
                        value={expense.amount}
                        onChange={(e) => handleChange("amount", e.target.value)}
                        label="Amount"
                        placeholder="Enter the amount"
                        type="number"
                  />

                  <Input
                        value={expense.date}
                        onChange={(e) => handleChange("date", e.target.value)}
                        label="Date"
                        placeholder=""
                        type="date"
                  />

                  <div className="flex justify-end mt-6">
                        <button 
                              type="button"
                              className="add-btn add-btn-fill"
                              onClick={() => onAddExpense(expense)}
                        >
                              Add Expense
                        </button>
                  </div>
            </div>
      )
}

export default AddExpenseForm;
