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
                     onChange={(target) => handleInputChange("source", target.value)}
                     label="Source"
                     placeholder="e.g. Salary, Gifts, Freelancing, etc."
                     type="text"
                 />

                 <Input
                     value={income.amount}
                     onChange={(target) => handleInputChange("amount", target.value)}
                     label="Amount"
                     placeholder=""
                     type="number"
                 />

                  <Input
                     value={income.date}
                     onChange={(target) => handleInputChange("date", target.value)}
                     label="Date"
                     placeholder="MM/DD/YYYY"
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
