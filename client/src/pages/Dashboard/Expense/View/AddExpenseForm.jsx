import React from 'react'
import EmojiPickerPopup from '../../../../components/EmojiPickerPopup';
import Input from '../../../../components/Input/Input';
import CustomDropdown from '../../Income/View/CustomDropdown';
import { toast } from 'react-hot-toast';

const AddExpenseForm = ({ onAddExpense }) => {

      const getTodayDate = () => {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');

            return `${year}-${month}-${day}`;
      };

      const todayDate = getTodayDate();

      const [expense, setExpense] = React.useState({
            icon:"",
            type:"Expense",
            category:"",
            amount:"",
            date: "",
            description:"",
      });

      const handleInputChange = (key, value) => setExpense({...expense, [key]: value});

      const handleAddExpense = () => {
            if (expense.date && expense.date > todayDate) {
                  toast.error('Enter Valid Date');
                  return;
            }

            onAddExpense(expense);
      };

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
                        max={todayDate}
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
                              onClick={handleAddExpense}
                        >
                              Add Expense
                        </button>
                  </div>

            </div>
      )
}

export default AddExpenseForm;
