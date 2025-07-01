import React from 'react'
import EmojiPickerPopup from "../EmojiPickerPopup";
import Input from "../Input/Input";
import CustomDropdown from '../Income/CustomDropdown';

const AddExpenseForm = ({ onAddExpense }) => {

      const [expense, setExpense] = React.useState({
            icon:"",
            type:"Expense",
            category:"",
            amount:"",
            date: "",
            cards:"",
            description:"",
      });

      const handleInputChange = (key, value) => setExpense({...expense, [key]: value});

      return (
            <div>

                  <EmojiPickerPopup
                        icon={expense.icon}
                        onSelect={(selectIcon) => handleInputChange("icon", selectIcon)}
                  />
                  <CustomDropdown
                        label="Expense Type"
                        data={["Income", "Expense"]}
                        defaultValue="Expense" // This will lock the dropdown to "Income"
                        placeholder="Select Type"
                  />
                  <Input
                        value={expense.category}
                        onChange={e => handleInputChange("category", e.target.value)}
                        label="Catagory"
                        placeholder="e.g. Salary, Gifts, Freelancing, Dinner, Shopping etc."
                        type="text"
                  />
                  <Input
                        value={expense.amount}
                        onChange={e => handleInputChange("amount", e.target.value)}
                        label="Amount"
                        type="number"
                  />
                  <Input
                        value={expense.date}
                        onChange={e => handleInputChange("date", e.target.value)}
                        label="Date"
                        type="date"
                  />
                  <Input
                        value={expense.source}
                        onChange={e => handleInputChange("cards", e.target.value)}
                        label="Cards"
                        placeholder="e.g. Debit Card, Credit Card etc."
                        type="text"
                  />
                  <Input
                        value={expense.source}
                        onChange={e => handleInputChange("description", e.target.value)}
                        label="Description"
                        placeholder=""
                        type="text"
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
