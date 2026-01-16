import React from 'react';
import Dashboard from './Dashboard';

const AdminDashboard = () => {
  return <Dashboard roleTitle="Admin" color="#0065A4" highlights={["User management", "Audit overview", "System settings"]} />;
};

export default AdminDashboard;
