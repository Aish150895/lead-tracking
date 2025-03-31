import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function NavBar() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();


  // Handle logout
  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container">
        <span className="navbar-brand">Lead Management System</span>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className="nav-link" to="/dashboard">
                Dashboard
              </Link>
            </li>

            <li className="nav-item">
              <Link className="nav-link" to="/">
                Lead Form now
              </Link>
            </li>
          </ul>
          
          {currentUser && (
            <ul className="navbar-nav">
              <li className="nav-item">
                <button className="btn btn-outline-light" onClick={handleLogout}>
                  Logout
                </button>
              </li>
            </ul>
          )}
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
