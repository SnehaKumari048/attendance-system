import { useState } from "react";
import API from "./api";

function App() {
  const [message, setMessage] = useState("");

  const testBackend = async () => {
    try {
      const res = await API.get("/");
      setMessage("Backend Connected ✅");
    } catch (err) {
      setMessage("Backend Not Reachable ❌");
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Attendance System 🚀</h1>
      <button onClick={testBackend}>
        Test Backend Connection
      </button>
      <p>{message}</p>
    </div>
  );
}

export default App;