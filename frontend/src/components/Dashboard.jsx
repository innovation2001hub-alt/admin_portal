import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = ({ roleTitle = 'Dashboard', color = '#1f6feb', highlights = [] }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header" style={{ borderBottomColor: color }}>
        <h1 style={{ color }}>{roleTitle} Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="welcome-card" style={{ borderLeftColor: color }}>
          <h2>Welcome back, {user?.first_name || user?.username}! 👋</h2>
          <p>You are signed in as <strong>{roleTitle}</strong>.</p>
        </div>

        <div className="user-info-card">
          <h3>User Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Full Name:</span>
              <span className="info-value">{user?.full_name || `${user?.first_name} ${user?.last_name}`.trim() || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Username:</span>
              <span className="info-value">{user?.username}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email:</span>
              <span className="info-value">{user?.email || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Employee ID (PF ID):</span>
              <span className="info-value">{user?.employee_id || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Designation:</span>
              <span className="info-value">{user?.designation || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Unit:</span>
              <span className="info-value">{user?.unit?.name || 'N/A'}</span>
            </div>
          </div>
        </div>

        {user?.roles && user.roles.length > 0 && (
          <div className="roles-card">
            <h3>Your Roles & Permissions</h3>
            <div className="roles-container">
              {user.roles.map((role) => (
                <div key={role.id} className="role-badge">
                  <span className="role-name">{role.name}</span>
                </div>
              ))}
            </div>
            <div className="roles-description">
              <p>You have been assigned the following roles in the system:</p>
              <ul>
                {user.roles.map((role) => (
                  <li key={role.id}>
                    <strong>{role.name}</strong>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {(!user?.roles || user.roles.length === 0) && (
          <div className="roles-card no-roles">
            <h3>Roles & Permissions</h3>
            <p>No roles have been assigned to your account yet. Please contact your administrator.</p>
          </div>
        )}

        <div className="placeholder-card" style={{ borderTopColor: color }}>
          <h3>Focus Areas</h3>
          <p>Key actions for your role:</p>
          <ul>
            {highlights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
