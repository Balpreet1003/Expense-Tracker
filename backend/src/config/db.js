const mongoose = require('mongoose');

//connnect to MongoDB
const connectDB = async () => {
      try {
            await mongoose.connect(process.env.MONGO_URI,{});
            console.log('MongoDB connected');
      }
      catch (error) {
            console.error('MongoDB connection error:', error);
            process.exit(1); // Exit the process with failure
      }
};

module.exports = connectDB;    