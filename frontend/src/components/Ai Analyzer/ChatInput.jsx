import React, { useState } from 'react';
import { RiSendPlaneFill } from "react-icons/ri";

const ChatInput = ({ onSend }) => {
    const [text, setText] = useState('');

    const submit = (e) => {
        e?.preventDefault();
        if (!text.trim()) return;
        onSend(text.trim());
        setText('');
    };

    return (
        <form onSubmit={submit} className="w-full flex items-center gap-3 focus:outline-none">
            <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Ask anything..."
                className="w-full bg-gray-100 focus:outline-none text-lg"
                aria-label="Message"
            />

            <button type="submit" className="py-2 px-4 rounded-xl bg-[#875cf5] text-white text-xl flex items-center justify-center gap-2 shadow hover:opacity-90">
                <RiSendPlaneFill />
            </button>
        </form>
    );
};

export default ChatInput;
