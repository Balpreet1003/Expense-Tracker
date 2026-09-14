import React, { useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { toast } from "react-hot-toast";

import DashboardLayout from "../../../../components/layout/DashboardLayout";
import ProfilePhotoSelector from "../../../../components/Input/ProfilePhotoSelector";
import Input from "../../../../components/Input/Input";

import { UserContext } from "../../../../context/UserContext";
import axiosInstance from "../../../../utils/axiosInstance";
import { API_PATHS } from "../../../../utils/apiPaths";
import { useUserAuth } from "../../../../hooks/useUserAuth";

const slugify = (value = "") =>
      String(value)
            .trim()
            .toLowerCase()
            .replace(/\s+/g, "-")
            .replace(/[^a-z0-9\-]/g, "");

function EditProfilePage() {
      useUserAuth();

      const { user, updateUser } = useContext(UserContext);
      const navigate = useNavigate();
      const location = useLocation();
      const { username } = useParams();

      const [fullName, setFullName] = useState("");
      const [email, setEmail] = useState("");
      const [password, setPassword] = useState("");

      const [profilePic, setProfilePic] = useState(null);
      const [initialProfileImageUrl, setInitialProfileImageUrl] = useState("");

      const [error, setError] = useState("");
      const [isSaving, setIsSaving] = useState(false);

      useEffect(() => {
            if (!user) {
                  return;
            }

            const raw =
                  user.username ||
                  user.fullName ||
                  user.email ||
                  "";

            const canonical = slugify(raw);

            if (
                  username &&
                  canonical &&
                  username !== canonical
            ) {
                  navigate(`/profile/${canonical}`, {
                        replace: true,
                        state: location.state,
                  });

                  return;
            }

            setFullName(user.fullName || "");
            setEmail(user.email || "");
            setPassword("");

            setProfilePic(user.profileImageUrl || null);
            setInitialProfileImageUrl(
                  user.profileImageUrl || ""
            );
      }, [
            user,
            username,
            navigate,
            location.state,
      ]);

      const hasChanges = useMemo(() => {
            const nameChanged =
                  fullName.trim() !==
                  (user?.fullName || "").trim();

            const passwordChanged =
                  password.trim().length > 0;

            const imageChanged =
                  profilePic instanceof File ||
                  profilePic instanceof Blob ||
                  (profilePic === null &&
                        !!initialProfileImageUrl);

            return (
                  nameChanged ||
                  passwordChanged ||
                  imageChanged
            );
      }, [
            fullName,
            password,
            profilePic,
            initialProfileImageUrl,
            user,
      ]);

      const resetFormToCurrentUser = () => {
            setFullName(user?.fullName || "");
            setEmail(user?.email || "");
            setPassword("");

            setProfilePic(
                  user?.profileImageUrl || null
            );

            setInitialProfileImageUrl(
                  user?.profileImageUrl || ""
            );

            setError("");
      };

      const handleCancel = () => {
            resetFormToCurrentUser();
      };

      const handleSubmit = async (event) => {
            event.preventDefault();

            setError("");

            if (!hasChanges) {
                  return;
            }

            if (!fullName.trim()) {
                  setError(
                        "Please enter your full name"
                  );
                  return;
            }

            if (
                  password.trim() &&
                  password.trim().length < 8
            ) {
                  setError(
                        "Password must be at least 8 characters long"
                  );
                  return;
            }

            setIsSaving(true);

            try {
                  const formData = new FormData();

                  /*
                   * Backend:
                   *
                   * full_name: str | None = Form(
                   *     alias="fullName"
                   * )
                   */
                  if (fullName.trim()) {
                        formData.append(
                              "fullName",
                              fullName.trim()
                        );
                  }

                  /*
                   * Backend:
                   *
                   * password: str | None = Form(...)
                   */
                  if (password.trim()) {
                        formData.append(
                              "password",
                              password.trim()
                        );
                  }

                  /*
                   * Backend:
                   *
                   * user_profile_image: UploadFile | None = File(
                   *     alias="profileImage"
                   * )
                   */
                  if (
                        profilePic instanceof File ||
                        profilePic instanceof Blob
                  ) {
                        formData.append(
                              "profileImage",
                              profilePic
                        );
                  }

                  const response =
                        await axiosInstance.patch(
                              API_PATHS.AUTH.PROFILE,
                              formData
                        );

                  /*
                   * Update user context with the
                   * updated user returned by FastAPI.
                   */
                  if (response.data) {
                        updateUser(response.data);

                        setFullName(
                              response.data.fullName || ""
                        );

                        setEmail(
                              response.data.email || ""
                        );

                        setPassword("");

                        setProfilePic(
                              response.data.profileImageUrl ||
                                    null
                        );

                        setInitialProfileImageUrl(
                              response.data.profileImageUrl ||
                                    ""
                        );
                  }

                  toast.success(
                        "Profile updated successfully"
                  );
            } catch (err) {
                  console.error(
                        "Failed to update profile:",
                        err
                  );

                  const message =
                        err.response?.data?.detail ||
                        err.response?.data?.message ||
                        "Something went wrong. Please try again.";

                  setError(message);
                  toast.error(message);
            } finally {
                  setIsSaving(false);
            }
      };

      return (
            <DashboardLayout>
                  <div className="mx-auto my-5 w-full px-4 md:px-0">
                        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm md:p-8">

                              <div className="mb-6">
                                    <h3 className="text-2xl font-semibold text-black">
                                          Edit Profile
                                    </h3>
                              </div>

                              <form
                                    onSubmit={handleSubmit}
                                    className="space-y-6"
                              >

                                    {/* Profile Image */}
                                    <ProfilePhotoSelector
                                          image={profilePic}
                                          setImage={setProfilePic}
                                          size="xl"
                                    />

                                    <div className="grid grid-cols-1 gap-4">

                                          {/* Full Name */}
                                          <Input
                                                value={fullName}
                                                onChange={({
                                                      target,
                                                }) =>
                                                      setFullName(
                                                            target.value
                                                      )
                                                }
                                                label="Full Name"
                                                placeholder="Enter your full name"
                                                type="text"
                                          />

                                          {/* Email - Cannot be updated */}
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

                                          {/* Password */}
                                          <Input
                                                value={password}
                                                onChange={({
                                                      target,
                                                }) =>
                                                      setPassword(
                                                            target.value
                                                      )
                                                }
                                                label="New Password"
                                                placeholder="Enter a new password"
                                                type="password"
                                          />

                                    </div>

                                    {error && (
                                          <p className="text-xs text-red-500">
                                                {error}
                                          </p>
                                    )}

                                    <div className="flex flex-row justify-left gap-3 pt-2">

                                          <button
                                                type="button"
                                                onClick={
                                                      handleCancel
                                                }
                                                disabled={
                                                      isSaving
                                                }
                                                className="my-1 w-xs rounded-xl border border-gray-300 px-5 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
                                          >
                                                Cancel
                                          </button>

                                          <button
                                                type="submit"
                                                disabled={
                                                      !hasChanges ||
                                                      isSaving
                                                }
                                                className="btn-primary max-w-xs disabled:cursor-not-allowed disabled:opacity-60"
                                          >
                                                {isSaving
                                                      ? "Saving..."
                                                      : "Save"}
                                          </button>

                                    </div>

                              </form>
                        </div>
                  </div>
            </DashboardLayout>
      );
}

export default EditProfilePage;