import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import AiChat from '../../components/Ai Analyzer/AiChat';

const AiAnalyzer = () => {
    return (
        <DashboardLayout activeMenu="AI Analyser">
            <div className=" mt-5 h-[calc(100vh-92px)] overflow-hidden">
                <AiChat />
            </div>
        </DashboardLayout>
    );
};

export default AiAnalyzer;
