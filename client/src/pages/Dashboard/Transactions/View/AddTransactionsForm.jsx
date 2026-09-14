import React from "react";
import EmojiPickerPopup from "../../../../components/EmojiPickerPopup";
import Input from "../../../../components/Input/Input";
import CustomDropdown from "../../Income/View/CustomDropdown";
import { toast } from "react-hot-toast";

const AddTransactionsForm = ({ onAddTransaction }) => {
  const getTodayDate = () => {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  };

  const todayDate = getTodayDate();

  const [transaction, setTransaction] = React.useState({
    icon: "",
    type: "",
    category: "",
    source: "",
    amount: "",
    date: "",
    description: "",
  });

  const handleInputChange = (key, value) => {
    setTransaction((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleAddTransaction = () => {
    if (!transaction.type) {
      toast.error("Transaction type is required");
      return;
    }

    if (transaction.type === "Expense") {
      if (!transaction.category.trim()) {
        toast.error("Category is required");
        return;
      }
    }

    if (transaction.type === "Income") {
      if (!transaction.source.trim()) {
        toast.error("Source is required");
        return;
      }
    }

    if (
      !transaction.amount ||
      isNaN(transaction.amount) ||
      Number(transaction.amount) <= 0
    ) {
      toast.error("Amount should be a valid number greater than 0");
      return;
    }

    if (!transaction.date) {
      toast.error("Date is required");
      return;
    }

    if (transaction.date > todayDate) {
      toast.error("Enter Valid Date");
      return;
    }

    onAddTransaction(transaction);
  };

  return (
    <div>
      <EmojiPickerPopup
        icon={transaction.icon}
        onSelect={(selectedIcon) =>
          handleInputChange("icon", selectedIcon)
        }
      />

      <CustomDropdown
        label="Transaction Type"
        data={["Income", "Expense"]}
        value={transaction.type}
        placeholder="Select Type"
        onChange={(e) =>
          handleInputChange("type", e.target.value)
        }
      />

      {/* Category / Source */}
      {transaction.type && (
        <Input
          value={
            transaction.type === "Expense"
              ? transaction.category
              : transaction.source
          }
          onChange={(e) =>
            handleInputChange(
              transaction.type === "Expense"
                ? "category"
                : "source",
              e.target.value
            )
          }
          label={
            transaction.type === "Expense"
              ? "Category"
              : "Source"
          }
          placeholder={
            transaction.type === "Expense"
              ? "e.g. Food, Transport, Entertainment, Rent, etc."
              : "e.g. Salary, Gifts, Freelancing, etc."
          }
          type="text"
        />
      )}

      <Input
        value={transaction.amount}
        onChange={(e) =>
          handleInputChange("amount", e.target.value)
        }
        label="Amount"
        type="number"
      />

      <Input
        value={transaction.date}
        onChange={(e) =>
          handleInputChange("date", e.target.value)
        }
        label="Date"
        type="date"
        max={todayDate}
      />

      <Input
        value={transaction.description}
        onChange={(e) =>
          handleInputChange("description", e.target.value)
        }
        label="Description"
        placeholder="Enter description"
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
  );
};

export default AddTransactionsForm;