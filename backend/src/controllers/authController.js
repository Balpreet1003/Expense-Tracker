const jwt= require("jsonwebtoken");
const bcrypt = require('bcryptjs');
const { query } = require('../config/db');
const { normalizeEmail, toUserResponse } = require('../utils/pgHelpers');

//generate JWT token 
const generateToken = (id) => {
      return jwt.sign({ id }, process.env.JWT_SECRET, {
            expiresIn: "30d",
      });
};

//register user 
exports.registerUser = async (req, res) => {
      const fullName = typeof req.body.fullName === 'string' ? req.body.fullName.trim() : '';
      const email = normalizeEmail(req.body.email);
      const password = typeof req.body.password === 'string' ? req.body.password : '';
      const profileImageUrl = typeof req.body.profileImageUrl === 'string' ? req.body.profileImageUrl.trim() : '';

      //validation :  check for missing fields
      if (!fullName || !email || !password) {
            return res.status(400).json({
                  message: "Please fill in all fields",
            });
      }

      try{
            //check if user already exists
            const existingUser = await query(
                  'SELECT id FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1',
                  [email]
            );

            if (existingUser.rowCount) {
                  return res.status(400).json({
                        message: "Email already in use",
                  });
            }

            const hashedPassword = await bcrypt.hash(password, 10);

            //create the user
            const userResult = await query(
                  `INSERT INTO users (full_name, email, password, profile_image_url)
                   VALUES ($1, $2, $3, $4)
                   RETURNING id, full_name, email, profile_image_url, created_at, updated_at`,
                  [fullName, email, hashedPassword, profileImageUrl]
            );

            const user = toUserResponse(userResult.rows[0]);

            res.status(201).json({
                  id: user.id,
                  user,
                  token: generateToken(user.id),
            });
      }

      catch (err){
            if (err.code === '23505') {
                  return res.status(400).json({
                        message: "Email already in use",
                  });
            }

            res.status(500).json({message: "Error registering user", error: err.message});
      }
};

//login user
exports.loginUser = async (req, res) => {
      const email = normalizeEmail(req.body.email);
      const password = typeof req.body.password === 'string' ? req.body.password : '';

      //validation :  check for missing fields
      if (!email || !password) {
            return res.status(400).json({
                  message: "Please fill all fields",
            });
      }

      try{
            //check if user exists
            const result = await query(
                  `SELECT id, full_name, email, password, profile_image_url, created_at, updated_at
                   FROM users
                   WHERE LOWER(email) = LOWER($1)
                   LIMIT 1`,
                  [email]
            );

            if (!result.rowCount) {
                  return res.status(400).json({
                        message: "Invalid credentials",
                  });
            }

            const userRow = result.rows[0];
            const isMatch = await bcrypt.compare(password, userRow.password);

            if (!isMatch) {
                  return res.status(400).json({
                        message: "Invalid credentials",
                  });
            }

            const user = toUserResponse(userRow);

            res.status(200).json({
                  id: user.id,
                  user,
                  token: generateToken(user.id),
            });
      }

      catch (err){
            res.status(500).json({message: "Error logging in user", error: err.message});
      }
};

//get user profile
exports.getUserInfo = async (req, res) => {
      try{
            const result = await query(
                  `SELECT id, full_name, email, profile_image_url, created_at, updated_at
                   FROM users
                   WHERE id = $1
                   LIMIT 1`,
                  [req.user.id]
            );

            if (!result.rowCount) {
                  return res.status(404).json({
                        message: "User not found",
                  });
            }

            res.status(200).json(toUserResponse(result.rows[0]));
      }
      catch (err){
            res.status(500).json({message: "Error getting user info", error: err.message});
      }
};

// update user profile
exports.updateUserInfo = async (req, res) => {
      const fullName = typeof req.body.fullName === 'string' ? req.body.fullName.trim() : '';
      const currentPassword = typeof req.body.currentPassword === 'string' ? req.body.currentPassword.trim() : '';
      const newPassword = typeof req.body.newPassword === 'string' ? req.body.newPassword.trim() : '';
      const profileImageUrl = typeof req.body.profileImageUrl === 'string' ? req.body.profileImageUrl.trim() : undefined;

      if (!fullName) {
            return res.status(400).json({
                  message: 'Please fill in all fields',
            });
      }

      try {
            const currentUserResult = await query(
                  `SELECT id, full_name, email, password, profile_image_url, created_at, updated_at
                   FROM users
                   WHERE id = $1
                   LIMIT 1`,
                  [req.user.id]
            );

            if (!currentUserResult.rowCount) {
                  return res.status(404).json({
                        message: 'User not found',
                  });
            }

            const currentUser = currentUserResult.rows[0];
            let hashedPassword = currentUser.password;

            if (newPassword) {
                  if (!currentPassword) {
                        return res.status(400).json({
                              message: 'Please enter your current password',
                        });
                  }

                  const isCurrentPasswordValid = await bcrypt.compare(currentPassword, currentUser.password);

                  if (!isCurrentPasswordValid) {
                        return res.status(400).json({
                              message: 'Current password is incorrect',
                        });
                  }

                  hashedPassword = await bcrypt.hash(newPassword, 10);
            }

            const nextProfileImageUrl = req.file?.path
                  ? req.file.path
                  : profileImageUrl !== undefined
                        ? profileImageUrl
                        : currentUser.profile_image_url || '';

            const updatedUserResult = await query(
                  `UPDATE users
                   SET full_name = $1,
                       email = $2,
                       password = $3,
                       profile_image_url = $4
                   WHERE id = $5
                   RETURNING id, full_name, email, profile_image_url, created_at, updated_at`,
                  [fullName, currentUser.email, hashedPassword, nextProfileImageUrl, req.user.id]
            );

            return res.status(200).json({
                  message: 'Profile updated successfully',
                  user: toUserResponse(updatedUserResult.rows[0]),
            });
      }
      catch (err) {
            res.status(500).json({message: 'Error updating user info', error: err.message});
      }
};