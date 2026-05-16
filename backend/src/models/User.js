const bcrypt = require('bcryptjs');
const { query } = require('../config/db');
const { normalizeEmail, toUserResponse } = require('../utils/pgHelpers');

const findUserByEmail = async (email) => {
    const normalizedEmail = normalizeEmail(email);

    if (!normalizedEmail) {
        return null;
    }

    const result = await query(
        `SELECT id, full_name, email, password, profile_image_url, created_at, updated_at
         FROM users
         WHERE LOWER(email) = LOWER($1)
         LIMIT 1`,
        [normalizedEmail]
    );

    return result.rows[0] || null;
};

const findUserById = async (id) => {
    const result = await query(
        `SELECT id, full_name, email, profile_image_url, created_at, updated_at
         FROM users
         WHERE id = $1
         LIMIT 1`,
        [id]
    );

    return result.rows[0] || null;
};

const createUser = async ({ fullName, email, password, profileImageUrl = '' }) => {
    const normalizedEmail = normalizeEmail(email);
    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await query(
        `INSERT INTO users (full_name, email, password, profile_image_url)
         VALUES ($1, $2, $3, $4)
         RETURNING id, full_name, email, profile_image_url, created_at, updated_at`,
        [fullName, normalizedEmail, hashedPassword, profileImageUrl]
    );

    return toUserResponse(result.rows[0]);
};

const comparePassword = async (candidatePassword, storedPassword) => bcrypt.compare(candidatePassword, storedPassword);

module.exports = {
    findUserByEmail,
    findUserById,
    createUser,
    comparePassword,
};