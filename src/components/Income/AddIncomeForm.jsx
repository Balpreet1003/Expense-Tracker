import React from 'react'
import Input from "../Input/Input"
import EmojiPickerPopup from '../EmojiPickerPopup';

const AddIncomeForm = ({onAddIncome}) => {

      const [income, setIncome] = React.useState({
            source: "",
            amount: "",
            date: "",
            icon: "",
      });

      const handleInputChange = (key, value) => setIncome({...income, [key]: value});

      return (
            <div>

                  <EmojiPickerPopup
                        icon={income.icon}
                        onSelect={(selectIcon) => handleInputChange("icon", selectIcon)}
                  />

                  <Input
                        value={income.source}
                        onChange={e => handleInputChange("source", e.target.value)}
                        label="Source"
                        placeholder="e.g. Salary, Gifts, Freelancing, etc."
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

export default AddIncomeForm
