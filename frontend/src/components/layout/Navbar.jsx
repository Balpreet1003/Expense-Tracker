import React, { useState, useContext, useRef, useEffect } from 'react';
import { HiOutlineMenu, HiOutlineX } from 'react-icons/hi';
import SideMenu from './SideMenu';
import CharAvatar from '../Components Cards/CharAvatar';
import { UserContext } from '../../context/UserContext';
import { LuChevronDown } from 'react-icons/lu';
import { USER_DROPDOWN_DATA } from '../../utils/user_dropdown_data';
import { useNavigate } from 'react-router-dom';

const Navbar = ({ activeMenu }) => {
      const [openSideMenu, setOpenSideMenu] = useState(false);
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
            <div className="sticky top-0 z-30">
                  <div className="flex justify-between items-center bg-white border border-b border-gray-200/50 backdrop-blur-[2px] py-4 px-7 h-[72px]">
                        {/* side bar toggle button */}
                        <div className="flex items-center gap-3">
                              <button
                                    className="block lg:hidden text-black"
                                    onClick={() => {
                                    setOpenSideMenu(!openSideMenu)
                                    }}
                              >
                                    {openSideMenu ? (
                                    <HiOutlineX className="text-2xl" />
                                    )
                                    : (
                                    <HiOutlineMenu className="text-2xl" />
                                    )}
                              </button>
                              <h2 className="text-lg font-medium text-black">Expense Tracker</h2>
                              {openSideMenu && (
                                    <div className="fixed top-[71px] -ml-7 bg-white min-[1024px]:hidden">
                                          <SideMenu activeMenu={activeMenu} />
                                    </div>
                              )}
                        </div>
                        {/* user profile button  */}
                        <button
                              ref={buttonRef}
                              className="flex items-center gap-4 border border-gray-200/50 px-3 py-1 rounded-full hover:bg-gray-100 transition-colors cursor-pointer max-[768px]:hidden"
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
                                          <LuChevronDown className="transform rotate-180 transition duration-600 ease-in-out text-xl" />
                                    ) : (
                                          <LuChevronDown className="transform transition duration-600 ease-in-out text-xl" />
                                    )
                              }
                        </button>
                  </div>
                  {/* user dropdown menu  */}
                  <div>
                        {
                              userDropdownOpen && (
                                    <div
                                          ref={dropdownRef}
                                          className="absolute right-[28px] top-[75px] bg-white border border-gray-200/50 rounded-lg shadow-lg p-4 w-53"
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
}
export default Navbar;
