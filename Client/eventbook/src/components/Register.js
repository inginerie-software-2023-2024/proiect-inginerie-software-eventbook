import { useState } from "react";
import "../styles/Form.css";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [username, setUsername] = useState("");

  const validateConfirmPassword = () => {
    setError("");
    if (password !== "" && confirmPassword !== "") {
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        return false;
      }
    }
    return true;
  };

  const isPasswordValid = (password) => {
    let errors = [];
    if (!/(?=.*[a-z])/.test(password)) {
      errors.push("Password must contain at least one lowercase letter.");
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      errors.push("Password must contain at least one uppercase letter.");
    }
    if (!/(?=.*\d)/.test(password)) {
      errors.push("Password must contain at least one digit.");
    }
    if (errors.length > 0) {
      setError(errors.join("\n"));
      return false;
    }
    return true;
  };

  const isEmailValid = (email) => {
    setError("");

    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address.");
      return false;
    }

    return true;
  };

  const register = async (e) => {
    e.preventDefault();
    if (!username) {
      setError("Username is required.");
      return;
    }
    if (
      !validateConfirmPassword() ||
      !isPasswordValid(password) ||
      !isEmailValid(email)
    ) {
      return;
    }
    try {
      const response = await fetch("http://127.0.0.1:8080/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(`${data.detail}`);
      }
      console.log(data);
      setEmail("");
      setPassword("");
      setConfirmPassword("");
      setUsername("");
      toast.success("Registered successfully. Redirecting to login...", {
        position: "top-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      setTimeout(() => {
        navigate("/authentication/login");
      }, 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <ToastContainer />
      <div className="form-container">
        <h1 className="form-title">Register</h1>
        <div className="auth-error">
          {error.split("\n").map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
        <form onSubmit={register} name="register-form">
          <div className="input-container">
            <input
              type="text"
              className="form-input"
              value={username}
              placeholder="Enter your username"
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              autoComplete="new-password"
              className="form-input"
              type="email"
              name="email"
              value={email}
              placeholder="Enter your email"
              required
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              onBlur={() => isEmailValid(email)}
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
                validateConfirmPassword();
              }}
              onBlur={() => isPasswordValid(password)}
            />
            <input
              className="form-input"
              autoComplete="new-password"
              type="password"
              name="confirmPassword"
              value={confirmPassword}
              required
              placeholder="Confirm password"
              onChange={(e) => {
                setConfirmPassword(e.target.value);
              }}
              onBlur={() => validateConfirmPassword()}
            />
            <button className="register-login-button" type="submit">
              <span>Register</span>
            </button>
            <p className="reddirect">
              Already a member? <Link to="/authentication/login">Login</Link>
            </p>
          </div>
        </form>
      </div>
    </>
  );
}

export default Register;
