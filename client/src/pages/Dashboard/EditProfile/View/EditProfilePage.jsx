import React, { useContext, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import DashboardLayout from '../../../../components/layout/DashboardLayout';
import ProfilePhotoSelector from '../../../../components/Input/ProfilePhotoSelector';
import Input from '../../../../components/Input/Input';
import { UserContext } from '../../../../context/UserContext';
import axiosInstance from '../../../../utils/axiosInstance';
import { API_PATHS } from '../../../../utils/apiPaths';
import { useUserAuth } from '../../../../hooks/useUserAuth';

const slugify = (value = '') =>
      String(value)
            .trim()
            .toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^a-z0-9\-]/g, '');

function EditProfilePage() {
      useUserAuth();

      const { user, updateUser } = useContext(UserContext);
      const navigate = useNavigate();
      const location = useLocation();
      const { username } = useParams();

      const [fullName, setFullName] = useState('');
      const [email, setEmail] = useState('');
      const [currentPassword, setCurrentPassword] = useState('');
      const [newPassword, setNewPassword] = useState('');
      const [profilePic, setProfilePic] = useState(null);
      const [initialProfileImageUrl, setInitialProfileImageUrl] = useState('');
      const [error, setError] = useState('');
      const [isSaving, setIsSaving] = useState(false);

      useEffect(() => {
            if (!user) {
                  return;
            }

            const raw = user.username || user.fullName || user.email || '';
            const canonical = slugify(raw);

            if (username && canonical && username !== canonical) {
                  navigate(`/profile/${canonical}`, { replace: true, state: location.state });
                  return;
            }

            setFullName(user.fullName || '');
            setEmail(user.email || '');
            setCurrentPassword('');
            setNewPassword('');
            setProfilePic(user.profileImageUrl || null);
            setInitialProfileImageUrl(user.profileImageUrl || '');
      }, [user, username, navigate, location.state]);

      const hasChanges = useMemo(() => {
            const trimmedName = fullName.trim();

            const imageChanged =
                  profilePic instanceof File ||
                  profilePic instanceof Blob ||
                  (profilePic === null && !!initialProfileImageUrl) ||
                  (typeof profilePic === 'string' && profilePic !== initialProfileImageUrl);
            const passwordChanged = newPassword.trim().length > 0;

            return (
                  trimmedName !== (user?.fullName || '').trim() ||
                  imageChanged ||
                  passwordChanged
            );
      }, [fullName, initialProfileImageUrl, newPassword, profilePic, user]);

      const getReturnPath = () => location.state?.from || '/dashboard';

      const resetFormToCurrentUser = () => {
            setFullName(user?.fullName || '');
            setEmail(user?.email || '');
            setCurrentPassword('');
            setNewPassword('');
            setProfilePic(user?.profileImageUrl || null);
            setInitialProfileImageUrl(user?.profileImageUrl || '');
            setError('');
      };

      const handleCancel = () => {
            resetFormToCurrentUser();
      };

      const handleSubmit = async (event) => {
            event.preventDefault();

            if (!hasChanges) {
                  return;
            }

            if (!fullName.trim()) {
                  setError('Please enter your full name');
                  return;
            }

            if (newPassword.trim() && newPassword.trim().length < 8) {
                  setError('Password must be at least 8 characters long');
                  return;
            }

            if (newPassword.trim() && !currentPassword.trim()) {
                  toast.error('Please enter your current password');
                  return;
            }

            setError('');
            setIsSaving(true);

            try {
                  const formData = new FormData();
                  formData.append('fullName', fullName.trim());

                  if (newPassword.trim()) {
                        formData.append('currentPassword', currentPassword.trim());
                        formData.append('newPassword', newPassword.trim());
                  }

                  if (profilePic instanceof File || profilePic instanceof Blob) {
                        formData.append('image', profilePic);
                  } else if (profilePic === null && initialProfileImageUrl) {
                        formData.append('profileImageUrl', '');
                  }

                  const response = await axiosInstance.put(API_PATHS.AUTH.UPDATE_PROFILE, formData, {
                        headers: {
                              'Content-Type': 'multipart/form-data',
                        },
                  });

                  if (response.data?.user) {
                        updateUser(response.data.user);
                  }

                  if (response.data?.user) {
                        setFullName(response.data.user.fullName || '');
                        setCurrentPassword('');
                        setNewPassword('');
                        setProfilePic(response.data.user.profileImageUrl || null);
                        setInitialProfileImageUrl(response.data.user.profileImageUrl || '');
                  }

                  toast.success('Profile updated successfully');
            } catch (err) {
                  const message = err.response?.data?.message || 'Something went wrong. Please try again.';
                  if (message === 'Current password is incorrect') {
                        toast.error(message);
                        return;
                  }

                  setError(message);
            } finally {
                  setIsSaving(false);
            }
      };

      return (
            <DashboardLayout>
                  <div className="mx-auto my-5 w-full px-4 md:px-0">
                        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm md:p-8">
                              <div className="mb-6">
                                    <h3 className="text-2xl font-semibold text-black">Edit Profile</h3>
                              </div>

                              <form onSubmit={handleSubmit} className="space-y-6">
                                    <ProfilePhotoSelector image={profilePic} setImage={setProfilePic} size="xl" />

                                    <div className="grid grid-cols-1 gap-4">
                                          <Input
                                                value={fullName}
                                                onChange={({ target }) => setFullName(target.value)}
                                                label="Full Name"
                                                placeholder="Enter your full name"
                                                type="text"
                                          />

                                          <Input
                                                value={email}
                                                label="Email Address"
                                                placeholder="Enter your email address"
                                                type="text"
                                                readOnly
                                                tabIndex={-1}
                                                aria-readonly="true"
                                                className="cursor-not-allowed bg-gray-50 text-slate-500"
                                          />

                                          <Input
                                                value={currentPassword}
                                                onChange={({ target }) => setCurrentPassword(target.value)}
                                                label="Current Password"
                                                placeholder="Enter your current password"
                                                type="password"
                                          />

                                          <Input
                                                value={newPassword}
                                                onChange={({ target }) => setNewPassword(target.value)}
                                                label="New Password"
                                                placeholder="Enter a new password"
                                                type="password"
                                          />
                                    </div>

                                    {error && <p className="text-xs text-red-500">{error}</p>}

                                    <div className="flex flex-row gap-3 pt-2 justify-left">
                                          <button
                                                type="button"
                                                onClick={handleCancel}
                                                className="rounded-xl border border-gray-300 px-5 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 w-xs my-1"
                                          >
                                                Cancel
                                          </button>

                                          <button
                                                type="submit"
                                                disabled={!hasChanges || isSaving}
                                                className="btn-primary disabled:cursor-not-allowed disabled:opacity-60 max-w-xs"
                                          >
                                                {isSaving ? 'Saving...' : 'Save'}
                                          </button>
                                    </div>
                              </form>
                        </div>
                  </div>
            </DashboardLayout>
      );
}

export default EditProfilePage;
