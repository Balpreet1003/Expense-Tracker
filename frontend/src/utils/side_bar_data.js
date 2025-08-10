import {
      LuLayoutDashboard,
      LuCoins,
      LuWalletMinimal,
      LuWalletCards,
      LuReceiptIndianRupee,
} from "react-icons/lu";
import { RiQuestionLine } from "react-icons/ri"

export const SIDE_MENU_DATA = [
      {
            id: "01",
            label: "Dashboard",
            icon: LuLayoutDashboard,
            path: "/dashboard",
      },
      {
            id: "02",
            label: "Income",
            icon: LuWalletMinimal,
            path: "/income",
      },
      {
            id: "03",
            label: "Expense",
            icon: LuCoins, 
            path: "/expense",
      },
      {
            id: "04",
            label: "Transactions",
            icon: LuReceiptIndianRupee, 
            path: "/transactions",
      },
      // {
      //       id: "05",
      //       label: "Cards",
      //       icon: LuWalletCards, 
      //       path: "/cards",
      // },
      // {
      //       id: "06",
      //       label: "Help Center",
      //       icon: RiQuestionLine, 
      //       path: "/help",
      // },
];
