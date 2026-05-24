const express = require('express');
const {protect} = require("../middleware/authMiddleware");
const upload = require("../middleware/uploadMiddleware");

const{
      registerUser,
      loginUser,
      getUserInfo,
      updateUserInfo,
} = require('../controllers/authController');

const router = express.Router();
router.post('/register', registerUser);  
router.post('/login', loginUser);
router.get('/getUser', protect, getUserInfo);
router.put('/update-profile', protect, upload.single('image'), updateUserInfo);
 
router.post("/upload-image", upload.single("image"), (req, res) => {
  if (!req.file || !req.file.path) {
    return res.status(400).json({ message: "No file uploaded" });
  }
  res.status(200).json({ imageUrl: req.file.path });
});

module.exports = router;  