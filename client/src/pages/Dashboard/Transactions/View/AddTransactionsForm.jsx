import React from 'react';
import EmojiPickerPopup from '../../../../components/EmojiPickerPopup';
import Input from '../../../../components/Input/Input';
import CustomDropdown from '../../Income/View/CustomDropdown';
import { toast } from 'react-hot-toast';

const AddTransactionsForm = ({onAddTransaction}) => {

      const getTodayDate = () => {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');

            return `${year}-${month}-${day}`;
      };

      const todayDate = getTodayDate();

      const [transaction, setTransaction] = React.useState({
            icon:"",
            type:"",
            category:"",
            amount:"",
            date: "",
            description:"",
      });

      const handleInputChange = (key, value) => setTransaction({...transaction, [key]: value});

      const handleAddTransaction = () => {
            if (transaction.date && transaction.date > todayDate) {
                  toast.error('Enter Valid Date');
                  return;
            }

            onAddTransaction(transaction);
      };

      return (
            <div>

                  <EmojiPickerPopup
                        icon={transaction.icon}
                        onSelect={(selectIcon) => handleInputChange("icon", selectIcon)}
                  />

                  <CustomDropdown
                        onChange={e => handleInputChange("type", e.target.value)}
                        label="Transaction Type"
                        data={["Income", "Expense"]}
                        value={transaction.type}
                        placeholder="Select Type"
                  />
                  {/* <CustomDropdown
                        label="Transaction Type"
                        data={["Income", "Expense"]}
                        defaultValue="Income" // This will lock the dropdown to "Income"
                        placeholder="Select Type"
                  /> */}
                  <Input
                        value={transaction.category}
                        onChange={e => handleInputChange("category", e.target.value)}
                        label="Catagory"
                        placeholder="e.g. Salary, Gifts, Freelancing, Dinner, Shopping etc."
                        type="text"
                  />
                  <Input
                        value={transaction.amount}
                        onChange={e => handleInputChange("amount", e.target.value)}
                        label="Amount"
                        type="number"
                  />
                  <Input
                        value={transaction.date}
                        onChange={e => handleInputChange("date", e.target.value)}
                        label="Date"
                        type="date"
                        max={todayDate}
                  />
                  <Input
                        value={transaction.source}
                        onChange={e => handleInputChange("description", e.target.value)}
                        label="Description"
                        placeholder=""
                        type="text"
                  />

                  <div className="flex justify-end mt-6">
                        <button 
                              type="button"
                              className="add-btn add-btn-fill"
                              onClick={handleAddTransaction}
                        >
                              Add Transaction
                        </button>
                  </div>

            </div>
      )
}

export default AddTransactionsForm;
