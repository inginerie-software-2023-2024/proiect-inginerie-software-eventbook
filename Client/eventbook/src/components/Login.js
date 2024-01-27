import { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/Form.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const login = async (e) => {
    e.preventDefault();
    setError("");

    const formData = new URLSearchParams();
    formData.append("grant_type", "");
    formData.append("username", username);
    formData.append("password", password);
    formData.append("scope", "");
    formData.append("client_id", "");
    formData.append("client_secret", "");

    try {
      const response = await fetch("http://127.0.0.1:8080/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Accept: "application/json",
        },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(`${data.detail}`);
      }
      localStorage.setItem("authToken", data.access_token);
      console.log(data);
      setUsername("");
      setPassword("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h1 className="form-title">Login</h1>
      {error && <div className="auth-error">{error}</div>}
      <form onSubmit={login} name="register-form">
        <div className="input-container">
          <input
            autoComplete="new-password"
            className="form-input"
            value={username}
            placeholder="Enter your username"
            required
            onChange={(e) => {
              setUsername(e.target.value);
            }}
          />
          <input
            className="form-input"
            autoComplete="new-password"
            name="password"
            type="password"
            value={password}
            required
            placeholder="Enter your password"
            onChange={(e) => {
              setPassword(e.target.value);
            }}
          />
          <button className="register-login-button" type="submit">
            <span>Login</span>
          </button>
          <p className="reddirect">
            Not a member yet?{" "}
            <Link to="/authentication/register">Register</Link>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;
