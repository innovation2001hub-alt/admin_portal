import React from 'react';
import Dashboard from './Dashboard';

const AdminDashboard = () => {
  return <Dashboard roleTitle="Admin" color="#d32f2f" highlights={["User management", "Audit overview", "System settings"]} />;
};

export default AdminDashboard;
