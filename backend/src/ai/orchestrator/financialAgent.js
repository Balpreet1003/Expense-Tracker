const { getMonthlySummary, getCategoryBreakdown, getTopExpenses, getExpenseTrend, getCardAnalytics, searchFinancialAdvice } = require('../tools');
const { postChatCompletion } = require('../../services/openai.service');
const { firstPassSystemPrompt, secondPassSystemPrompt } = require('../prompts/systemPrompt');

const toolRegistry = {
      getMonthlySummary,
      getCategoryBreakdown,
      getTopExpenses,
      getExpenseTrend,
      getCardAnalytics,
      searchFinancialAdvice,
};

const toolDefinitions = [
      {
            type: 'function',
            function: {
                  name: 'getMonthlySummary',
                  description: 'How much did I spend last month?',
                  parameters: {
                        type: 'object',
                        properties: {
                              month: {
                                    type: 'string',
                                    description: 'Month in YYYY-MM format. Defaults to last month when omitted.',
                              },
                        },
                        additionalProperties: false,
                  },
            },
      },
      {
            type: 'function',
            function: {
                  name: 'getCategoryBreakdown',
                  description: 'Where did I spend my money?',
                  parameters: {
                        type: 'object',
                        properties: {
                              month: {
                                    type: 'string',
                                    description: 'Month in YYYY-MM format. Defaults to last month when omitted.',
                              },
                        },
                        additionalProperties: false,
                  },
            },
      },
      {
            type: 'function',
            function: {
                  name: 'getTopExpenses',
                  description: 'What were my largest expenses?',
                  parameters: {
                        type: 'object',
                        properties: {
                              limit: {
                                    type: 'integer',
                                    minimum: 1,
                                    maximum: 20,
                                    description: 'Maximum number of expenses to return.',
                              },
                        },
                        additionalProperties: false,
                  },
            },
      },
      {
            type: 'function',
            function: {
                  name: 'getExpenseTrend',
                  description: 'Compare this month with last month.',
                  parameters: {
                        type: 'object',
                        properties: {
                              month: {
                                    type: 'string',
                                    description: 'Month in YYYY-MM format. Defaults to the current month when omitted.',
                              },
                        },
                        additionalProperties: false,
                  },
            },
      },
      {
            type: 'function',
            function: {
                  name: 'getCardAnalytics',
                  description: 'Which card is used most?',
                  parameters: {
                        type: 'object',
                        properties: {
                              limit: {
                                    type: 'integer',
                                    minimum: 1,
                                    maximum: 20,
                                    description: 'Maximum number of cards to return.',
                              },
                        },
                        additionalProperties: false,
                  },
            },
      },
      {
            type: 'function',
            function: {
                  name: 'searchFinancialAdvice',
                  description: 'How can I save more money?',
                  parameters: {
                        type: 'object',
                        properties: {
                              query: {
                                    type: 'string',
                                    description: 'Search query for advice documents.',
                              },
                              limit: {
                                    type: 'integer',
                                    minimum: 1,
                                    maximum: 10,
                                    description: 'Maximum number of advice documents to return.',
                              },
                        },
                        required: ['query'],
                        additionalProperties: false,
                  },
            },
      },
];

const parseJson = (value, fallback = {}) => {
      if (!value || typeof value !== 'string') {
            return fallback;
      }

      try {
            return JSON.parse(value);
      }
      catch {
            return fallback;
      }
};

const executeToolCall = async (userId, toolCall, userPrompt) => {
      const toolName = toolCall?.function?.name;
      const tool = toolRegistry[toolName];

      if (!tool) {
            throw new Error(`Unsupported tool: ${toolName}`);
      }

      const argumentsPayload = parseJson(toolCall?.function?.arguments, {});

      if (toolName === 'searchFinancialAdvice' && !argumentsPayload.query) {
            argumentsPayload.query = userPrompt;
      }

      if (toolName === 'getMonthlySummary' && !argumentsPayload.month) {
            argumentsPayload.month = undefined;
      }

      if (toolName === 'getCategoryBreakdown' && !argumentsPayload.month) {
            argumentsPayload.month = undefined;
      }

      return tool({
            userId,
            ...argumentsPayload,
      });
};

const runFinancialAgent = async ({ userId, prompt }) => {
      const firstPass = await postChatCompletion({
            messages: [
                  {
                        role: 'system',
                        content: firstPassSystemPrompt,
                  },
                  {
                        role: 'user',
                        content: prompt,
                  },
            ],
            tools: toolDefinitions,
            tool_choice: 'auto',
      });

      const firstChoice = firstPass?.choices?.[0];
      const toolCalls = firstChoice?.message?.tool_calls || [];

      if (!toolCalls.length) {
            const directAnswer = typeof firstChoice?.message?.content === 'string'
                  ? firstChoice.message.content.trim()
                  : '';

            if (directAnswer) {
                  return directAnswer;
            }
      }

      const financialData = {};
      const knowledge = [];

      for (const toolCall of toolCalls) {
            const toolName = toolCall?.function?.name;
            const result = await executeToolCall(userId, toolCall, prompt);

            if (toolName === 'searchFinancialAdvice') {
                  knowledge.push(...(Array.isArray(result) ? result : []));
            }
            else {
                  financialData[toolName] = result;
            }
      }

      const secondPass = await postChatCompletion({
            messages: [
                  {
                        role: 'system',
                        content: secondPassSystemPrompt,
                  },
                  {
                        role: 'user',
                        content: JSON.stringify({
                              userQuery: prompt,
                              financialData,
                              knowledge,
                        }, null, 2),
                  },
            ],
      });

      const finalAnswer = secondPass?.choices?.[0]?.message?.content;

      return typeof finalAnswer === 'string' && finalAnswer.trim()
            ? finalAnswer.trim()
            : 'I could not generate a response from the available financial data.';
};

module.exports = {
      runFinancialAgent,
      toolDefinitions,
};