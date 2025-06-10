import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../../components/layout/AuthLayout';
import Input from '../../components/Input/Input';
import { validateEmail } from '../../utils/helper';
import axiosInstance from '../../utils/axiosInstance';
import { API_PATHS } from '../../utils/apiPaths';
import { UserContext } from '../../context/UserContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const {updateUser} = useContext(UserContext);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            setError("Please enter an email address");
            return;
        }

        if (!validateEmail(email)) {
            setError("Please enter a valid email address");
            return;
        }

        if (!password) {
            setError("Please enter a password");
            return;
        }

        setError(""); // Clear any previous errors

        // Login API call
        try {
            const response = await axiosInstance.post(API_PATHS.AUTH.LOGIN, {
                email,
                password,
            });
            const { token, user } = response.data;

            if(token) {
                localStorage.setItem('token', token);
                updateUser(user);
                navigate('/dashboard');
            }
        }
        catch (err) {
            if (err.response && err.response.data.message) {
                setError(err.response.data.message);
            } else {
                setError("Something went wrong. Please try again.");
            }
        }
    };

    return (
        <AuthLayout>
            <div className='lg:w-[70%] md:h-full flex flex-col justify-center'>
                <h3 className='text-xl font-semibold text-black'>Welcome Back</h3>
                <p className='text-xs text-slate-700 mt-[5px] mb-6'>
                    Please enter your details to log in
                </p>
                <form onSubmit={handleSubmit} className='flex flex-col gap-4'>
                    <Input
                        type="text"
                        label="Email Address"
                        placeholder="Enter your email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <Input
                        type="password"
                        label="Password"
                        placeholder="Min 8 characters"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    {error && <p className='text-red-500 text-xs pb-2.5'>{error}</p>}
                    <button type='submit' className='btn-primary'>
                        LOGIN
                    </button>
                    <p className='text-[13px] text-slate-800 mt-3'>
                        Don't have an account?{' '}
                        <Link className="font-medium text-primary underline" to="/signUp">
                            Sign Up
                        </Link>
                    </p>
                </form>
            </div>
        </AuthLayout>
    );
};

export default Login;