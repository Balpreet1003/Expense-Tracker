import axios from 'axios';
import {BASE_URL } from './apiPaths';

const axiosInstance = axios.create({
      baseURL: BASE_URL,
      timeout: 100000,
      headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
      },
});

//Request Insterceptor
axiosInstance.interceptors.request.use(
      (config) => {
            const accesstoken = localStorage.getItem('token');
            if (accesstoken) {
                  config.headers.Authorization = `Bearer ${accesstoken}`;
            }
            return config;
      },
      (error) => {
            return Promise.reject(error);
      }
);

//Response Insterceptor
axiosInstance.interceptors.response.use(
      (response) => {
            return response;
      },
      (error) => {
            //Handle common errore globally
            if (error.response) {
                  if(error.response.status === 401) {
                        window.location.href = '/login';
                  }
                  else if(error.response.status === 500) {
                        console.error("Server Error. Please try again later.");
                  }
            }
            else if(error.code === "ECONNABORTED") {
                  console.error("Request timedout. Please try again.");
            }
            return Promise.reject(error);
      }
);

export default axiosInstance; 