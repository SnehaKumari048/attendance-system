import axios from "axios";

const API = axios.create({
  baseURL: "https://attendance-system-gnyf.onrender.com"
});

export default API;