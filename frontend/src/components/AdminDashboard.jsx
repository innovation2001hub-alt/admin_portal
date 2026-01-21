import React from 'react';
import Dashboard from './Dashboard';

const AdminDashboard = () => {
  return <Dashboard roleTitle="Admin" color="#738d9e" highlights={["User management", "Audit overview", "System settings"]} />;
};

export default AdminDashboard;
