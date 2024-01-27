import { useLocation } from "react-router-dom";
import Login from "./Login";
import Register from "./Register";
import "../styles/Auth.css";

function Authentication() {
  const location = useLocation();
  const isLogin = location.pathname.includes("login");

  return (
    <>
      <div className="auth-container">
        {isLogin ? (
          <div className="login-container">
            <Login />
          </div>
        ) : (
          <div className="register-container">
            <Register />
          </div>
        )}
      </div>
    </>
  );
}

export default Authentication;
