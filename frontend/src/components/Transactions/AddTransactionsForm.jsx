import React from 'react';
import EmojiPickerPopup from '../EmojiPickerPopup';
import Input from '../Input/Input';
import CustomDropdown from '../Income/CustomDropdown';

const AddTransactionsForm = ({onAddTransaction}) => {

      const [transaction, setTransaction] = React.useState({
            icon:"",
            type:"",
            category:"",
            amount:"",
            date: "",
            cards:"",
            description:"",
      });

      const handleInputChange = (key, value) => setTransaction({...transaction, [key]: value});

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
                  />
                  <Input
                        value={transaction.source}
                        onChange={e => handleInputChange("cards", e.target.value)}
                        label="Cards"
                        placeholder="e.g. Debit Card, Credit Card etc."
                        type="text"
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
                              onClick={() => onAddTransaction(transaction)}
                        >
                              Add Transaction
                        </button>
                  </div>

            </div>
      )
}

export default AddTransactionsForm;
