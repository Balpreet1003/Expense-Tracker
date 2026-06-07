import React, { useState, useContext, useRef, useEffect } from 'react';
import { RiRobot2Line } from "react-icons/ri";
import { UserContext } from '../../../../context/UserContext'; 
import ReactMarkdown from "react-markdown";
import CharAvatar from '../../../../components/Components_Cards/CharAvatar';


const ChatBubble = ({ role, text, chatAnimationVal }) => {
    const isUser = role === 'user';
    const { user, clearUser } = useContext(UserContext);
    const [displayedText, setDisplayedText] = useState("");

    useEffect(() => {
        if (!text) return;

        let index = 0;
        if(chatAnimationVal){
                const interval = setInterval(() => {
                setDisplayedText(text.slice(0, index));
                index++;
                if (index > text.length) clearInterval(interval);
            }, 10);

            return () => clearInterval(interval);
        }
        else{
            setDisplayedText(text);
        }
    }, [text]);

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-start`}>
            {!isUser && (
                <div className="mr-3">
                    <div className="lg:w-9 w-7 lg:h-9 h-7 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center text-white lg:text-xl text-lg">
                        <RiRobot2Line/>
                    </div>
                </div>
            )}

            <div className={`${isUser ? 'rounded-tl-xl rounded-br-xl rounded-bl-xl bg-[#9183f7]' : 'text-gray-900 rounded-tr-xl rounded-br-xl rounded-bl-xl  bg-gray-100'} mt-5 px-4 py-3 max-w-[70%] shadow-sm lg:text-base text-sm`}> 
                <div className="whitespace-pre-wrap"><ReactMarkdown>{role!=="user" ? displayedText : text}</ReactMarkdown></div>
            </div>

            {isUser && (
                <div className="ml-3">
                    {user?.profileImageUrl ? (
                        <img
                                src={user?.profileImageUrl}
                                alt="Profile"
                                className="lg:w-9 w-7 lg:h-9 h-7 bg-slate-400 rounded-full object-cover"
                        />
                    ) : (
                        <CharAvatar
                            fullName={user?.fullName}
                            width="w-7"
                            height="h-7"
                            style="text-base"
                        />
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatBubble;
