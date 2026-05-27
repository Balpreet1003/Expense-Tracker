const { getFinancialAnalyticsSnapshot } = require('../services/financialAnalyticsService');
const { searchFinancialAdviceDocs } = require('../services/vector.service');
const { runFinancialAgent, buildFallbackReply } = require('../ai/orchestrator/financialAgent');

exports.analyzeTransactions = async (req, res) => {
      try {
            const prompt = typeof req.body?.prompt === 'string' ? req.body.prompt.trim() : '';

            if (!prompt) {
                  return res.status(400).json({ message: 'Prompt is required' });
            }

            const analytics = await getFinancialAnalyticsSnapshot(req.user.id);
            const adviceDocs = await searchFinancialAdviceDocs(prompt, 3);

            try {
                  const reply = await runFinancialAgent({
                        userId: req.user.id,
                        prompt,
                  });

                  return res.json({ reply });
            }
            catch (openAiError) {
                  console.error('OpenAI tool flow unavailable, using fallback summary:', openAiError);
                  return res.json({ reply: buildFallbackReply(analytics, adviceDocs, prompt) });
            }
      }
      catch (error) {
            console.error('AI analysis error:', error);
            return res.status(500).json({ message: 'Failed to analyze transactions' });
      }
};