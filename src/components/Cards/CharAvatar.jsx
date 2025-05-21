import React from 'react'
import { getInitials } from '../../utils/helper'

const CharAvatar = ({fullName, width, height, style}) => {
      return (
            <div className={`${width || "w-12"} ${height || "h-12"}  ${style || ""} flex items-center justify-center bg-gray-100 rounded-full text-gray-900 font-medium`}>
                  {getInitials(fullName || "")}
            </div>
      )
}

export default CharAvatar
