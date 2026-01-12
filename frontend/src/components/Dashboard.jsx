import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Admin Portal Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome back, {user?.first_name || user?.username}! 👋</h2>
          <p>You have successfully logged in to the Admin Portal.</p>
        </div>

        <div className="user-info-card">
          <h3>User Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Username:</span>
              <span className="info-value">{user?.username}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email:</span>
              <span className="info-value">{user?.email || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Employee ID:</span>
              <span className="info-value">{user?.employee_id || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Unit:</span>
              <span className="info-value">{user?.unit?.name || 'N/A'}</span>
            </div>
          </div>
        </div>

        <div className="placeholder-card">
          <h3>Coming Soon</h3>
          <p>More features will be added here:</p>
          <ul>
            <li>User Management</li>
            <li>Unit Hierarchy</li>
            <li>Approval Requests</li>
            <li>Audit Logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
