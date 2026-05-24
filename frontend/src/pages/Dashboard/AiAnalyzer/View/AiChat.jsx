import React, { useEffect, useRef, useState } from 'react';
import ChatHeader from './ChatHeader';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import axiosInstance from '../../../../utils/axiosInstance';
import { API_PATHS } from '../../../../utils/apiPaths';

const AiChat = () => {
    const [messages, setMessages] = useState(() => {
        try {
            const raw = localStorage.getItem('ai_chat_messages');
            if (raw) return JSON.parse(raw);
        } catch (e) {
            console.error('Failed to parse stored messages:', e);
        }
        return [
            { id: 1, role: 'bot', text: "Hello! I'm your AI assistant. I can analyze your transactions and help you understand your spending patterns. What would you like to know?" }
        ];
    });
    const [chatAnimation, setChatAnimation] = useState(false);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    // Persist messages to localStorage whenever they change
    useEffect(() => {
        try {
            localStorage.setItem('ai_chat_messages', JSON.stringify(messages));
        } catch (e) {
            console.error('Failed to save messages to localStorage:', e);
        }
    }, [messages]);

    const sendMessage = async (text) => {
        if (!text || !text.trim()) return;
        const userMsg = { id: Date.now(), role: 'user', text };
        setMessages(prev => [...prev, userMsg]);
        setLoading(true);

        try {
            setChatAnimation(true);
            const response = await axiosInstance.post(API_PATHS.AI.ANALYZE, {
                prompt: text.trim(),
            });

            const replyText = response?.data?.reply ?? 'Sorry, I could not generate a response right now.';

            const botMsg = { id: Date.now() + 1, role: 'bot', text: replyText };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            console.error('Error getting AI response:', err);
            setMessages(prev => [...prev, { 
                id: Date.now() + 2, 
                role: 'bot', 
                text: 'Sorry, I encountered an error while analyzing your data. Please try again.' 
            }]);
        } finally {
            setLoading(false);
        }
    };

  return (
    <div className="my-5 xl:px-30 lg:px-20 md:px-20 sm:px-10 px-0 flex flex-col justify-between">
        <div className="h-[72px]">
            <ChatHeader />
        </div>
        <div className="pt-6 px-6 lg:px-12 flex flex-col h-[calc(100vh-256px)]">
            <div className="flex-1 overflow-y-auto pr-2 space-y-6">
                {messages.map(msg => (
                    <ChatBubble key={msg.id} role={msg.role} text={msg.text} chatAnimationVal={chatAnimation} controlAnimation={()=>{setChatAnimation(false)}}/>
                ))}
                {loading && (
                    <div className="flex items-center text-sm text-gray-500">AI is typing<span className="animate-pulse">...</span></div>
                )}
                <div ref={scrollRef} />
            </div>

        </div>
        <div className="h-[72px] px-6 flex items-center bg-gray-100 rounded-full">
            <div className="w-full">
                <ChatInput onSend={sendMessage} />
            </div>
        </div>
    </div>
  );
};

export default AiChat;
