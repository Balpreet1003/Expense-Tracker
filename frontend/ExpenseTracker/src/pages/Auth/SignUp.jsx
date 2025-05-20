import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../../components/layout/AuthLayout';
import Input from '../../components/Input/Input';
import { validateEmail } from '../../utils/helper';
import ProfilePhotoSelector from '../../components/Input/ProfilePhotoSelector';
import axiosInstance from '../../utils/axiosInstance';
import { API_PATHS } from '../../utils/apiPaths';
import { UserContext } from '../../context/UserContext';
import uploadImage from '../../utils/uploadImage';

const SignUp = () => {
  const [profilePic, setProfilePic] = useState(null);
  const[fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const[error, setError] = useState('');

  const {updateUser} = useContext(UserContext);
  const navigate = useNavigate();

  //handle sign up 
  const handleSignUp = async (e) => {
    e.preventDefault();

    if (!fullName) {
      setError("Please enter your full name");
      return;
    }

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

    let profileImageUrl = "";

    // SignUp API call
    try {

      //upload image if present
      if (profilePic) {
        const imgUploadRes = await uploadImage(profilePic);
        profileImageUrl = imgUploadRes.imageUrl || "";
      }

      const response = await axiosInstance.post(API_PATHS.AUTH.REGISTER, {
        fullName,
        email,
        password,
        profileImageUrl
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
  }

  return (
    <AuthLayout>
        <div className='lg:w-[100%] h-auto md:h-full mt-10 md:mt-0 flex flex-col justify-center'>
            
            <h3 className='text-xl font-semibold text-black'>
              Create an Account
            </h3>

            <p className='text-xs text-slate-700 mt-[5px] mb-6'>
              Join us today by entering your details below
            </p>

            <form onSubmit={handleSignUp}>

                <ProfilePhotoSelector
                  image={profilePic}
                  setImage={setProfilePic}
                />

                <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'>
                  <Input 
                    value={fullName}
                    onChange={({target})=> setFullName(target.value)}
                    label="Full Name"
                    placeholder="Enter your full name"
                    type="text"
                  />

                  <Input
                    type="text"
                    label="Email Address"
                    placeholder="Enter your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />

                  <div className='col-span-2'>
                    <Input
                      type="password"
                      label="Password"
                      placeholder="Min 8 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>

                {error && <p className='text-red-500 text-xs pb-2.5'>{error}</p>}
                <button type='submit' className='btn-primary '>
                    SIGN UP
                </button>
                <p className='text-[13px] text-slate-800 mt-3'>
                    Already have an account?{' '}
                    <Link className="font-medium text-primary underline" to="/login">
                        Login
                    </Link>
                </p>

            </form>
        </div>

    </AuthLayout>
  )
}

export default SignUp