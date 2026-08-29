import moment from "moment";
import { API_PATHS } from "../../../../utils/apiPaths";
import axiosInstance from "../../../../utils/axiosInstance";

export const addThousandsSeparator = (number) => {
      if(number === null || isNaN(number)) return "";

      const [integerPart, fractionPart] = String(number).split(".");
      const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

      return fractionPart? `${formattedInteger}.${fractionPart}` : formattedInteger;
};

export const prepareExpenseChartData = (data= []) => {
      const chartData =data.map((item) => ({
            category: item.category,
            amount: item.amount,
      }));
 
      return chartData;
}

export const uploadImage = async (imageFile) => {
      const formData = new FormData();
      formData.append("image", imageFile);
      
      try {
            const response = await axiosInstance.post(API_PATHS.IMAGE.UPLOAD_IMAGE, formData, {
                  headers: {
                        "Content-Type": "multipart/form-data",
                  },
            });
            return response.data;
      } 
      catch (error) {
            console.error("Error uploading image:", error);
            throw error;
      } 
}