const { Pool } = require('pg');
require('dotenv').config();

if (!process.env.DB_URL) {
      throw new Error('DB_URL is not configured');
}

const pool = new Pool({
      connectionString: process.env.DB_URL,
      ssl: {
            rejectUnauthorized: false,
      },
      max: 20,
      idleTimeoutMillis: 30000,
});

pool.on('connect', () => {});

pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
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

      CREATE UNIQUE INDEX IF NOT EXISTS unique_default_card_per_user
            ON cards (user_id)
            WHERE is_default = TRUE;

      CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
      CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
      CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

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

            // await client.query(schemaSql);
      }
      catch (error) {
            console.error('PostgreSQL connection error:', error);
            throw error;
      }
      finally {
            if (client) {
                  client.release();
            }
      }
};

module.exports = {
      pool,
      connectDB,
      query: (text, params) => pool.query(text, params),
};