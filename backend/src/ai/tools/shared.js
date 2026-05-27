const normalizeMonthKey = (value = new Date()) => {
      if (typeof value === 'string' && /^\d{4}-\d{2}$/.test(value)) {
            return value;
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return new Date().toISOString().slice(0, 7);
      }

      return date.toISOString().slice(0, 7);
};

const getMonthDate = (monthKey) => new Date(`${monthKey}-01T00:00:00.000Z`);

const getPreviousMonthKey = (monthKey) => {
      const date = getMonthDate(monthKey);
      date.setUTCMonth(date.getUTCMonth() - 1);
      return date.toISOString().slice(0, 7);
};

const getMonthLabel = (monthKey) => {
      const date = getMonthDate(monthKey);
      return date.toLocaleString('en-US', {
            month: 'short',
            timeZone: 'UTC',
      });
};

module.exports = {
      normalizeMonthKey,
      getMonthDate,
      getPreviousMonthKey,
      getMonthLabel,
};