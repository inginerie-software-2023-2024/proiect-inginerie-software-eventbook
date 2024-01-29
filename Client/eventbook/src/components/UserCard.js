import AccountIcon from "@mui/icons-material/AccountBox";
import { Link } from "react-router-dom";

function UserCard({ user }) {
  return (
    <Link to={`/user/${user.username}`} className="no-underline-link user-card">
      <AccountIcon id="person" />
      <div className="username-and-email">
        <p className="username">{user.username}</p>
        <p className="email">{user.email}</p>
      </div>
    </Link>
  );
}

export default UserCard;
