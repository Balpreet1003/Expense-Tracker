import React, {useContext, useEffect, useRef, useState} from 'react';
import { SIDE_MENU_DATA } from '../../utils/side_bar_data';
import { useNavigate } from 'react-router-dom';
import { UserContext } from '../../context/UserContext';
import CharAvatar from '../Components Cards/CharAvatar';
import { LuChevronUp } from 'react-icons/lu';
import { USER_DROPDOWN_DATA } from '../../utils/user_dropdown_data';

const SideMenu = ({activeMenu}) => {

      const [userDropdownOpen, setUserDropdownOpen] = useState(false);
      const { user, clearUser } = useContext(UserContext);
      const navigate = useNavigate();

      const dropdownRef = useRef(null);
      const buttonRef = useRef(null);

      useEffect(() => {
            function handleClickOutside(event) {
                  if (
                        userDropdownOpen &&
                        dropdownRef.current &&
                        !dropdownRef.current.contains(event.target) &&
                        buttonRef.current &&
                        !buttonRef.current.contains(event.target)
                  ) {
                        setUserDropdownOpen(false);
                  }
            }
            if (userDropdownOpen) {
                  document.addEventListener('mousedown', handleClickOutside);
            } else {
                  document.removeEventListener('mousedown', handleClickOutside);
            }
            return () => {
                  document.removeEventListener('mousedown', handleClickOutside);
            };
      }, [userDropdownOpen]);

      const handelClick = (route) => {
      if (route === "logout") {
            handelLogout();
            return;
      }
      navigate(route);
      };

      const handelLogout = () => {
            localStorage.clear();
            clearUser();
            navigate("/login");
      };

      return (
            <div className="flex w-64 h-[calc(100vh-72px)] bg-white border-r border-gray-200/50 p-5 sticky top-[72px] z-20">
                  <div className="flex flex-col justify-between">
                        {/* side bar pages option */}
                        <div>
                              {SIDE_MENU_DATA.map((item, index) => (
                                    <button
                                          key={`menu_${index}`}
                                          className={
                                                `w-full flex items-center gap-4 text-[15px] 
                                                ${activeMenu === item.label ? "text-white bg-[#875cf5]" : ""} py-3 px-6 rounded-lg mb-3 cursor-pointer`
                                          }
                                          onClick={() => handelClick(item.path)}
                                    >
                                          <item.icon className="text-xl" />
                                          {item.label}
                                    </button>
                              ))}
                        </div>
                        {/* user profile  */}
                        <button
                              ref={buttonRef}
                              className="flex items-center gap-4 border border-gray-200/50 px-3 py-1 rounded-full hover:bg-gray-100 transition-colors cursor-pointer min-[768px]:hidden"
                              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                        >
                              <div className="flex items-center gap-[5px]">
                                    {user?.profileImageUrl ? (
                                    <img
                                          src={user?.profileImageUrl}
                                          alt="Profile"
                                          className="w-7 h-7 bg-slate-400 rounded-full object-cover"
                                    />
                                    ) : (
                                          <CharAvatar
                                                fullName={user?.fullName}
                                                width="w-7"
                                                height="h-7"
                                                style="text-base"
                                          />
                                    )}
                                    <span className="text-gray-900 font-medium text-base">
                                          {user?.fullName}
                                    </span>
                              </div>
                              {
                                    userDropdownOpen ? (
                                          <LuChevronUp className="transform rotate-180 transition duration-600 ease-in-out text-xl" />
                                    ) : (
                                          <LuChevronUp className="transform transition duration-600 ease-in-out text-xl" />
                                    )
                              }

                        </button>
                  </div>
                  {/* dropdown menu */}
                  <div>
                        {
                        userDropdownOpen && (
                              <div
                                    ref={dropdownRef}
                                    className="absolute left-[20px] bottom-[64px] bg-white border border-gray-200/50 rounded-lg shadow-lg p-4 w-53"
                              >
                                    <ul>
                                          {USER_DROPDOWN_DATA.map((item, index) => (
                                                <button
                                                      key={`menu_${index}`}
                                                      className="flex gap-2 item-center py-2 px-3 hover:bg-gray-100 cursor-pointer w-full text-left rounded-lg"
                                                      onClick={() => handelClick(item.path)}
                                                >
                                                      <item.icon className="text-xl" />
                                                      {item.label}
                                                </button>
                                          ))}
                                    </ul>
                              </div>
                        )
                        }
                  </div>
            </div>
      )
};

export default SideMenu;
