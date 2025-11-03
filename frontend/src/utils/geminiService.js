import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);

export async function generateAIResponse(prompt, transactions) {
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
        const input = `
        You are a financial assistant.
        Here are the user's recent transactions:
        ${JSON.stringify(transactions, null, 2)}

        User's query:
        ${prompt}

        Please analyze or respond helpfully in a clear, concise way. Alway show money in rupees format (₹).
        `;
        const result = await model.generateContent(input);
        const response = await result.response;
        return response.text();
    } catch (error) {
        console.error("Error getting AI response:", error);
        throw error;
    }
}
