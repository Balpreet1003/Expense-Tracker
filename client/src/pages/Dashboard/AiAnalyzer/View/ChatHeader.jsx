import React from 'react';
import { RiRobot2Line } from "react-icons/ri";

const ChatHeader = () => {
    return (
        <div className="flex items-center justify-between px-6 py-4 h-full bg-gray-100 rounded-full">
            <div className="flex items-center gap-4">
                <div className="lg:w-12 w-10 lg:h-12 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center text-white text-2xl font-bold">
                    <RiRobot2Line/>
                </div>
                <div>
                    <div className="font-semibold text-sm lg:text-lg">AI Assistant</div>
                    <div className="text-xs text-green-500">Online</div>
                </div>
            </div>
        </div>
    );
};

export default ChatHeader;