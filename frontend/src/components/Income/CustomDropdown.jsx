import React from 'react';

const CustomDropdown = ({ data = [], label, defaultValue, value, onChange, placeholder }) => {
      const isDisabled = !!defaultValue;
      const selectedValue = defaultValue !== undefined && defaultValue !== "" ? defaultValue : value;

      return (
            <div>
                  {label && <label className='text-[13px] text-slate-800'>{label}</label>}
                  <div className='input-box'>
                        <select
                              className="w-full"
                              value={selectedValue || ""}
                              onChange={onChange}
                              disabled={isDisabled}
                        >
                              {!selectedValue && <option value="">{placeholder || "Select"}</option>}
                              {data.map((item, idx) => (
                                    <option key={idx} value={item}>
                                          {item}
                                    </option>
                              ))}
                        </select>
                  </div>
            </div>
      );
};

export default CustomDropdown;
