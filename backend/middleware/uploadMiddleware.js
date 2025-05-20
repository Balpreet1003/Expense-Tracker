const multer = require('multer');

//configure storage
const storage = multer.diskStorage({
      destination: (req, file, cb) => {
            cb(null, 'uploads/');
      },
      filename: (req, file, cb) => {
            cb(null,`${Date.now()}-${file.originalname}`);
      }
});

//file filter
const fileFilter = (req, file, cb) => {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
      } else {
            cb(new Error('Invalid file type. Only JPEG, JPG and PNG are allowed.'), false);
      }
};

const upload = multer({storage, fileFilter});

module.exports = upload; 