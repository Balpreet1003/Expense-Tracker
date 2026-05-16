const normalizeEmail = (email) => {
      if (typeof email !== 'string') {
            return '';
      }

      return email.trim().toLowerCase();
};

const normalizeCardNumber = (cardNumber) => {
      if (typeof cardNumber !== 'string') {
            return '';
      }

      return cardNumber.replace(/[^0-9]/g, '');
};

const parseBoolean = (value) => {
      if (typeof value === 'boolean') {
            return value;
      }

      if (typeof value === 'string') {
            return ['true', '1', 'yes', 'on'].includes(value.trim().toLowerCase());
      }

      return false;
};

const parsePositiveAmount = (value) => {
      const amount = Number(value);

      if (!Number.isFinite(amount) || amount <= 0) {
            return null;
      }

      return amount;
};

const parseIntegerId = (value) => {
      const parsed = Number(value);

      if (!Number.isInteger(parsed) || parsed <= 0) {
            return null;
      }

      return parsed;
};

const normalizeCardType = (cardType) => {
      if (typeof cardType !== 'string') {
            return '';
      }

      const compact = cardType.trim().toLowerCase();
      const mapping = {
            visa: 'Visa',
            mastercard: 'MasterCard',
            americanexpress: 'AmericanExpress',
            rupee: 'RuPay',
            rupay: 'RuPay',
            other: 'Other',
      };

      return mapping[compact] || cardType.trim();
};

const toUserResponse = (row) => {
      if (!row) {
            return null;
      }

      return {
            id: row.id,
            _id: row.id,
            fullName: row.full_name,
            email: row.email,
            profileImageUrl: row.profile_image_url || '',
            createdAt: row.created_at,
            updatedAt: row.updated_at,
      };
};

const toCardResponse = (row) => {
      if (!row) {
            return null;
      }

      return {
            id: row.id,
            _id: row.id,
            userId: row.user_id,
            cardName: row.card_name,
            cardNumber: row.card_number,
            cardType: row.card_type,
            expiryDate: row.expiry_date,
            cvv: row.cvv,
            bankName: row.bank_name,
            isDefault: row.is_default,
            createdAt: row.created_at,
            updatedAt: row.updated_at,
      };
};

const toTransactionResponse = (row) => {
      if (!row) {
            return null;
      }

      return {
            id: row.id,
            _id: row.id,
            userId: row.user_id,
            cardId: row.card_id,
            icon: row.icon || '',
            type: row.type,
            category: row.category,
            amount: Number(row.amount),
            date: row.date,
            cards: row.cards || row.card_name || '',
            description: row.description || '',
            createdAt: row.created_at,
            updatedAt: row.updated_at,
      };
};

const toTransactionExcelRow = (row) => ({
      icon: row.icon || '',
      type: row.type,
      category: row.category,
      amount: Number(row.amount),
      date: row.date,
      cards: row.cards || row.card_name || '',
      description: row.description || '',
});

module.exports = {
      normalizeEmail,
      normalizeCardNumber,
      parseBoolean,
      parsePositiveAmount,
      parseIntegerId,
      normalizeCardType,
      toUserResponse,
      toCardResponse,
      toTransactionResponse,
      toTransactionExcelRow,
};