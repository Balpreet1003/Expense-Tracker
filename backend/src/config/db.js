const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
      connectionString: process.env.DB_URL,
      ssl: {
            rejectUnauthorized: false,
      },
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
});

pool.on('connect', () => {});

pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
      process.exit(-1);
});

const schemaSql = `
      CREATE OR REPLACE FUNCTION trigger_set_timestamp()
      RETURNS TRIGGER AS $$
      BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;

      DO $$
      BEGIN
            CREATE TYPE transaction_type AS ENUM ('income', 'expense');
      EXCEPTION
            WHEN duplicate_object THEN NULL;
      END $$;

      DO $$
      BEGIN
            CREATE TYPE card_type AS ENUM ('Visa', 'MasterCard', 'AmericanExpress', 'RuPay', 'Other');
      EXCEPTION
            WHEN duplicate_object THEN NULL;
      END $$;

      CREATE EXTENSION IF NOT EXISTS vector;

      CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            profile_image_url TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            card_name VARCHAR(100) NOT NULL,
            card_number VARCHAR(19) NOT NULL UNIQUE,
            card_type card_type NOT NULL,
            expiry_date DATE NOT NULL,
            cvv VARCHAR(10) NOT NULL,
            bank_name VARCHAR(100) NOT NULL,
            is_default BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_cards_user
                  FOREIGN KEY (user_id)
                  REFERENCES users(id)
                  ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            card_id INT,
            cards TEXT DEFAULT '',
            icon VARCHAR(100),
            type transaction_type NOT NULL,
            category VARCHAR(100) NOT NULL,
            amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
            date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            description TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_transactions_user
                  FOREIGN KEY (user_id)
                  REFERENCES users(id)
                  ON DELETE CASCADE,
            CONSTRAINT fk_transactions_card
                  FOREIGN KEY (card_id)
                  REFERENCES cards(id)
                  ON DELETE SET NULL
      );

      ALTER TABLE transactions
            ADD COLUMN IF NOT EXISTS cards TEXT DEFAULT '';

      CREATE TABLE IF NOT EXISTS financial_advice_docs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT,
            content TEXT NOT NULL,
            embedding VECTOR(1536),
            created_at TIMESTAMPTZ DEFAULT NOW()
      );

      CREATE UNIQUE INDEX IF NOT EXISTS unique_default_card_per_user
            ON cards (user_id)
            WHERE is_default = TRUE;

      CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
      CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

      CREATE UNIQUE INDEX IF NOT EXISTS idx_financial_advice_docs_title
            ON financial_advice_docs (title);

      DO $$
      BEGIN
            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_matviews
                  WHERE schemaname = current_schema()
                        AND matviewname = 'monthly_financial_summary'
            ) THEN
                  CREATE MATERIALIZED VIEW monthly_financial_summary AS
                  SELECT
                        user_id,
                        DATE_TRUNC('month', date) AS month,
                        SUM(
                              CASE
                                    WHEN type = 'income'
                                    THEN amount
                                    ELSE 0
                              END
                        ) AS total_income,
                        SUM(
                              CASE
                                    WHEN type = 'expense'
                                    THEN amount
                                    ELSE 0
                              END
                        ) AS total_expense
                  FROM transactions
                  GROUP BY
                        user_id,
                        DATE_TRUNC('month', date);
            END IF;
      END $$;

      DO $$
      BEGIN
            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_matviews
                  WHERE schemaname = current_schema()
                        AND matviewname = 'category_summary'
            ) THEN
                  CREATE MATERIALIZED VIEW category_summary AS
                  SELECT
                        user_id,
                        DATE_TRUNC('month', date) AS month,
                        category,
                        SUM(amount) AS total_amount
                  FROM transactions
                  GROUP BY
                        user_id,
                        DATE_TRUNC('month', date),
                        category;
            END IF;
      END $$;

      DO $$
      BEGIN
            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_matviews
                  WHERE schemaname = current_schema()
                        AND matviewname = 'card_spending_summary'
            ) THEN
                  CREATE MATERIALIZED VIEW card_spending_summary AS
                  SELECT
                        user_id,
                        card_id,
                        SUM(amount) AS total_spent
                  FROM transactions
                  WHERE type = 'expense'
                        AND card_id IS NOT NULL
                  GROUP BY
                        user_id,
                        card_id;
            END IF;
      END $$;

      CREATE UNIQUE INDEX IF NOT EXISTS idx_monthly_financial_summary_user_month
            ON monthly_financial_summary (user_id, month);

      CREATE UNIQUE INDEX IF NOT EXISTS idx_category_summary_user_month_category
            ON category_summary (user_id, month, category);

      CREATE UNIQUE INDEX IF NOT EXISTS idx_card_spending_summary_user_card
            ON card_spending_summary (user_id, card_id);

      DO $$
      BEGIN
            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_trigger
                  WHERE tgname = 'set_timestamp_users'
            ) THEN
                  CREATE TRIGGER set_timestamp_users
                        BEFORE UPDATE ON users
                        FOR EACH ROW
                        EXECUTE FUNCTION trigger_set_timestamp();
            END IF;

            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_trigger
                  WHERE tgname = 'set_timestamp_cards'
            ) THEN
                  CREATE TRIGGER set_timestamp_cards
                        BEFORE UPDATE ON cards
                        FOR EACH ROW
                        EXECUTE FUNCTION trigger_set_timestamp();
            END IF;

            IF NOT EXISTS (
                  SELECT 1
                  FROM pg_trigger
                  WHERE tgname = 'set_timestamp_transactions'
            ) THEN
                  CREATE TRIGGER set_timestamp_transactions
                        BEFORE UPDATE ON transactions
                        FOR EACH ROW
                        EXECUTE FUNCTION trigger_set_timestamp();
            END IF;
      END $$;
`;

const connectDB = async () => {
      let client;

      try {
            client = await pool.connect();
            const result = await client.query('SELECT NOW()');
            console.log('PostgreSQL connection test successful:', result.rows[0]);

            await client.query(schemaSql);

            await refreshAnalyticsMaterializedViews();
      }
      catch (error) {
            console.error('PostgreSQL connection error:', error);
            process.exit(1);
      }
      finally {
            if (client) {
                  client.release();
            }
      }
};

const refreshAnalyticsMaterializedViews = async () => {
      const viewNames = [
            'monthly_financial_summary',
            'category_summary',
            'card_spending_summary',
      ];

      for (const viewName of viewNames) {
            await pool.query(`REFRESH MATERIALIZED VIEW CONCURRENTLY ${viewName}`);
      }
};

module.exports = {
      pool,
      connectDB,
      refreshAnalyticsMaterializedViews,
      query: (text, params) => pool.query(text, params),
};