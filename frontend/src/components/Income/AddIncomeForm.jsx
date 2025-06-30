import React from 'react';
import Input from "../Input/Input";
import EmojiPickerPopup from '../EmojiPickerPopup';
import CustomDropdown from './CustomDropdown';

const AddIncomeForm = ({onAddIncome}) => {

      const [income, setIncome] = React.useState({
            icon:"",
            type:"Income",
            category:"",
            amount:"",
            date: "",
            cards:"",
            description:"",
      });

      const handleInputChange = (key, value) => setIncome({...income, [key]: value});

      return (
            <div>

                  <EmojiPickerPopup
                        icon={income.icon}
                        onSelect={(selectIcon) => handleInputChange("icon", selectIcon)}
                  />
                  <CustomDropdown
                        label="Transaction Type"
                        data={["Income", "Expense"]}
                        defaultValue="Income"
                        placeholder="Select Type"
                  />
                  <Input
                        value={income.category}
                        onChange={e => handleInputChange("category", e.target.value)}
                        label="Catagory"
                        placeholder="e.g. Salary, Gifts, Freelancing, Dinner, Shopping etc."
                        type="text"
                  />
                  <Input
                        value={income.amount}
                        onChange={e => handleInputChange("amount", e.target.value)}
                        label="Amount"
                        type="number"
                  />
                  <Input
                        value={income.date}
                        onChange={e => handleInputChange("date", e.target.value)}
                        label="Date"
                        type="date"
                  />
                  <Input
                        value={income.cards}
                        onChange={e => handleInputChange("cards", e.target.value)}
                        label="Cards"
                        placeholder="e.g. Debit Card, Credit Card etc."
                        type="text"
                  />
                  <Input
                        value={income.description}
                        onChange={e => handleInputChange("description", e.target.value)}
                        label="Description"
                        placeholder=""
                        type="text"
                  />

                  <div className="flex justify-end mt-6">
                        <button 
                              type="button"
                              className="add-btn add-btn-fill"
                              onClick={() => onAddIncome(income)}
                        >
                              Add Income
                        </button>
                  </div>

            </div>
      )
}

export default AddIncomeForm;
