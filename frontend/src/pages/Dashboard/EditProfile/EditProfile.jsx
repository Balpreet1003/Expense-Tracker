import React, { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { UserContext } from '../../../context/UserContext';

const slugify = (value = '') =>
  String(value)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-]/g, '');

const EditProfile = () => {
  const { user } = useContext(UserContext);
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const raw = user.username || user.fullName || user.email || '';
  const canonical = slugify(raw) || '';

  if (!canonical) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Navigate 
      to={`/profile/${canonical}`} 
      replace state={location.state}
  />;
};

export default EditProfile;
