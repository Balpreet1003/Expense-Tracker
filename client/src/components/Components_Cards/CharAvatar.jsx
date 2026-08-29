import React from 'react'

const CharAvatar = ({fullName, width, height, style}) => {

      const getInitials = (name) => {
            if (!name) return "";
            const names = name.split(" ");
            let initials = "";

            for(let i = 0 ; i < Math.min(names.length, 2); i++) {
                  initials += names[i][0];
            }

            return initials.toUpperCase();
      };

      return (
            <div className={`${width || "w-12"} ${height || "h-12"}  ${style || ""} flex items-center justify-center bg-gray-100 rounded-full text-gray-900 font-medium`}>
                  {getInitials(fullName || "")}
            </div>
      )
}

export default CharAvatar;
