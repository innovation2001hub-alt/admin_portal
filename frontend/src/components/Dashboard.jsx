import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import CreateRequestForm from './CreateRequestForm';
import MyRequestsList from './MyRequestsList';
import ApprovalQueue from './ApprovalQueue';
import RequestReview from './RequestReview';
import AllRequests from './AllRequests';
import ApprovalMetrics from './ApprovalMetrics';
import UserManagement from './UserManagement';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout, isMaker, isChecker, isAdmin, isSuperAdmin } = useAuth();
  const navigate = useNavigate();
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [currentTab, setCurrentTab] = useState('overview');
  const [token, setToken] = useState(localStorage.getItem('token'));
  
  // Set initial tab based on user role once user is loaded
  React.useEffect(() => {
    if (user) {
      if (isSuperAdmin()) setCurrentTab('user-management');
      else if (isMaker() || isAdmin()) setCurrentTab('create');
      else if (isChecker()) setCurrentTab('queue');
    }
  }, [user, isSuperAdmin, isMaker, isAdmin, isChecker]);

  // Show loading state if user is not loaded yet
  if (!user) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleRequestApprovalReject = () => {
    setRefreshTrigger((prev) => prev + 1);
    setSelectedRequest(null);
  };

  const getRoleTitle = () => {
    if (isSuperAdmin()) return 'Super Administrator';
    if (isAdmin()) return 'Administrator';
    if (isChecker()) return 'Checker/Approver';
    if (isMaker()) return 'Request Maker';
    return 'Dashboard';
  };

  const getRoleColor = () => {
    if (isSuperAdmin()) return '#9c27b0';
    if (isAdmin()) return '#f64747';
    if (isChecker()) return '#2cce7d';
    if (isMaker()) return '#1f6feb';
    return '#1f6feb';
  };

  const getAvailableTabs = () => {
    const tabs = [];
    
    if (isSuperAdmin()) {
      tabs.push({ id: 'user-management', label: '👥 User Management', icon: 'users' });
    }
    
    if (isMaker() || isAdmin()) {
      tabs.push(
        { id: 'create', label: '✚ Create Request', icon: 'create' },
        { id: 'my-requests', label: '📋 My Requests', icon: 'requests' }
      );
    }
    if (isChecker() || isAdmin()) {
      tabs.push({ id: 'queue', label: '✓ Approval Queue', icon: 'queue' });
    }
    if (isAdmin()) {
      tabs.push(
        { id: 'all-requests', label: '📊 All Requests', icon: 'all' },
        { id: 'metrics', label: '📈 Metrics', icon: 'metrics' }
      );
    }
    if (tabs.length === 0) {
      tabs.push({ id: 'overview', label: '👋 Overview', icon: 'overview' });
    }
    return tabs;
  };

  const availableTabs = getAvailableTabs();

  return (
    <div className="dashboard-container">
      <div className="dashboard-header" style={{ borderBottomColor: getRoleColor() }}>
        <div className="dashboard-header-logo">
          <img src="/sbi_logo.png" alt="SBI Logo" />
          <h1>{getRoleTitle()} Dashboard</h1>
        </div>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        {/* Welcome Card */}
        <div className="welcome-card" style={{ borderLeftColor: getRoleColor() }}>
          <h2>Welcome back, {user?.first_name || user?.username}! 👋</h2>
          <p>You are signed in as <strong>{getRoleTitle()}</strong>.</p>
        </div>

        {/* User Info Card */}
        <div className="user-info-card">
          <h3>User Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Full Name:</span>
              <span className="info-value">{user?.full_name || `${user?.first_name} ${user?.last_name}`.trim() || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Employee ID (PF ID):</span>
              <span className="info-value">{user?.employee_id || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Unit:</span>
              <span className="info-value">{user?.unit?.name || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email:</span>
              <span className="info-value">{user?.email || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Roles Card */}
        {user?.roles && user.roles.length > 0 && (
          <div className="roles-card">
            <h3>Your Roles & Permissions</h3>
            <div className="roles-container">
              {user.roles.map((role) => (
                <div key={role.id} className="role-badge" style={{ borderColor: getRoleColor() }}>
                  <span className="role-name">{role.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tabs Navigation */}
        {availableTabs.length > 0 && (
          <div className="dashboard-tabs">
            <div className="tabs-header">
              {availableTabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab-button ${currentTab === tab.id ? 'active' : ''}`}
                  onClick={() => setCurrentTab(tab.id)}
                  style={currentTab === tab.id ? { borderBottomColor: getRoleColor() } : {}}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="tabs-content">
              {/* User Management Tab (Super Admin only) */}
              {currentTab === 'user-management' && isSuperAdmin() && (
                <UserManagement token={token} />
              )}

              {/* Create Request Tab */}
              {currentTab === 'create' && (isMaker() || isAdmin()) && (
                <CreateRequestForm
                  onSuccess={() => {
                    setCurrentTab('my-requests');
                  }}
                />
              )}

              {/* My Requests Tab */}
              {currentTab === 'my-requests' && (isMaker() || isAdmin()) && (
                <MyRequestsList key={`my-requests-${refreshTrigger}`} />
              )}

              {/* Approval Queue Tab */}
              {currentTab === 'queue' && (isChecker() || isAdmin()) && (
                <ApprovalQueue
                  key={`queue-${refreshTrigger}`}
                  onSelectRequest={(request) => {
                    setSelectedRequest(request);
                  }}
                />
              )}

              {/* All Requests Tab */}
              {currentTab === 'all-requests' && isAdmin() && (
                <AllRequests key={`all-${refreshTrigger}`} />
              )}

              {/* Metrics Tab */}
              {currentTab === 'metrics' && isAdmin() && (
                <ApprovalMetrics key={`metrics-${refreshTrigger}`} />
              )}
            </div>
          </div>
        )}

        {/* Request Review Modal */}
        {selectedRequest && (isChecker() || isAdmin()) && (
          <RequestReview
            request={selectedRequest}
            onClose={() => setSelectedRequest(null)}
            onApproveReject={handleRequestApprovalReject}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
