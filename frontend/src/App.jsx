import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import Login from './pages/Auth/View/Login';
import SignUp from './pages/Auth/View/SignUp';
import Home from './pages/Dashboard/Home/Home';
import Income from './pages/Dashboard/Income/Income';
import Expense from './pages/Dashboard/Expense/Expense';
import UserProvider from './context/UserContext';
import EditProfilePage from './pages/Dashboard/EditProfile/View/EditProfilePage';
import EditProfile from './pages/Dashboard/EditProfile/EditProfile';
import Transactions from './pages/Dashboard/Transactions/Transactions';
import AiAnalyzer from './pages/Dashboard/AiAnalyzer/AiAnalyzer';
import { Toaster } from'react-hot-toast';

const App = () => {
  return (
    <UserProvider>
      <div>
        <Router>
          <Routes>
            <Route path="/" element={<Root />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signUp" element={<SignUp />} />
            <Route path="/dashboard" element={<Home />} />
            <Route path="/income" element={<Income />} />
            <Route path="/expense" element={<Expense />} />
            <Route path="/profile" element={<EditProfile />} />
            <Route path="/profile/:username" element={<EditProfilePage />} />
            <Route path="/ai-analyser" element={<AiAnalyzer/>} />
            <Route path="/transactions" element={<Transactions />} />
          </Routes>
        </Router>
      </div>

      <Toaster
        toastOptions={{
          className: "",
          style: {
            fontSize: "13px"
          },
        }}
      />
    </UserProvider>
  )
}

export default App;


const Root = () => {
  // check if token exists in local storage
  const isAuthenticated = !!localStorage.getItem("token");

  //redirect to dashboard if authenticated, otherwise redirect to login
  return isAuthenticated ? (
    <Navigate to="/dashboard" />
  ) : (
    <Navigate to="/login" />
  );
};
