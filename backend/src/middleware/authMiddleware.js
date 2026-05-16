const jwt= require('jsonwebtoken');
const { query } = require('../config/db');
const { toUserResponse } = require('../utils/pgHelpers');

exports.protect = async (req, res, next) => {
      let token = req.headers.authorization?.split(" ")[1];
      if(!token) {
            return res.status(401).json({
                  message: "Not authorized, no token",
            });
      } 
      try { 
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            const result = await query(
                  `SELECT id, full_name, email, profile_image_url, created_at, updated_at
                   FROM users
                   WHERE id = $1
                   LIMIT 1`,
                  [decoded.id]
            );

            if (!result.rowCount) {
                  return res.status(401).json({
                        message: "Not authorized, user not found",
                  });
            }

            req.user = toUserResponse(result.rows[0]);
            next();
      }
      catch(err) {
            res.status(401).json({
                  message: "Not authorized, token failed",
            });
      }
};