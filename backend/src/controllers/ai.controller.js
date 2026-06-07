const { runFinancialAgent, buildFallbackReply } = require('../ai/orchestrator/financialAgent');
const { classifyIntent } = require('../ai/classifier/intentClassifier');
const { getFinancialAnalyticsSnapshot } = require('../services/financialAnalyticsService');
const { searchFinancialAdviceDocs } = require('../services/vector.service');
const { Intent, detectIntent, isFinancialQuery } = require('../ai/router/intentRouter');

const buildDirectResponse = (intent) => {
      if (intent === Intent.GREETING) {
            return 'Hello! I can help you analyze your finances, track spending trends, identify large expenses, and suggest ways to save money.';
      }

      if (intent === Intent.HELP) {
            return [
                  'You can ask things like:',
                  '',
                  '• Summarize my spending this month',
                  '• Compare this month with last month',
                  '• Where am I spending the most?',
                  '• How can I save money?',
            ].join('\n');
      }

      return 'I can help with financial questions like spending summaries, trend analysis, category breakdowns, savings advice, and card analysis.';
};

const resolveIntentForPrompt = async (prompt) => {
      const classifierResult = await classifyIntent(prompt);
      const routerIntent = detectIntent(prompt);
      const normalizedPrompt = typeof prompt === 'string' ? prompt.trim().toLowerCase() : '';

      const directChatIntents = [Intent.GREETING, Intent.HELP, Intent.GENERAL_CHAT];
      const financialSignal = isFinancialQuery(normalizedPrompt);

      if (routerIntent === Intent.INCOME_SOURCES) {
            return routerIntent;
      }

      if (financialSignal) {
            if (routerIntent !== Intent.GENERAL_CHAT) {
                  return routerIntent;
            }

            if (classifierResult.intent && !directChatIntents.includes(classifierResult.intent)) {
                  return classifierResult.intent;
            }

            return Intent.SPENDING_ANALYSIS;
      }

      if (directChatIntents.includes(classifierResult.intent) && !directChatIntents.includes(routerIntent)) {
            return routerIntent;
      }

      return classifierResult.intent;
};

exports.analyzeTransactions = async (req, res) => {
      try {
            const prompt = typeof req.body?.prompt === 'string'
                  ? req.body.prompt.trim()
                  : typeof req.body?.query === 'string'
                        ? req.body.query.trim()
                        : typeof req.body?.userQuery === 'string'
                              ? req.body.userQuery.trim()
                              : '';

            if (!prompt) {
                  return res.status(400).json({ message: 'Prompt is required' });
            }

            const resolvedIntent = await resolveIntentForPrompt(prompt);

            if (resolvedIntent === Intent.GREETING || resolvedIntent === Intent.HELP || resolvedIntent === Intent.GENERAL_CHAT) {
                  return res.json({ reply: buildDirectResponse(resolvedIntent) });
            }

            try {
                  const reply = await runFinancialAgent({
                        userId: req.user.id,
                        prompt,
                        intent: resolvedIntent,
                  });

                  return res.json({ reply });
            }
            catch (geminiError) {
                  console.error('Gemini tool flow unavailable, using fallback summary:', geminiError);
                  const analytics = await getFinancialAnalyticsSnapshot(req.user.id);
                  const knowledgeQuery = analytics.highestCategory && analytics.highestCategory !== 'None'
                        ? `${analytics.highestCategory} expense reduction strategies`
                        : 'budgeting and saving strategies';
                  const adviceDocs = await searchFinancialAdviceDocs(knowledgeQuery, 5);
                  return res.json({ reply: buildFallbackReply(analytics, adviceDocs, prompt) });
            }
      }
      catch (error) {
            console.error('AI analysis error:', error);
            return res.status(500).json({ message: 'Failed to analyze transactions' });
      }
};