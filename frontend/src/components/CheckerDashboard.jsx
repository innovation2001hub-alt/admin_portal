import React from 'react';
import Dashboard from './Dashboard';

const CheckerDashboard = () => {
  return <Dashboard roleTitle="Checker" color="#388e3c" highlights={["Review approvals", "Validate data", "Sign-off items"]} />;
};

export default CheckerDashboard;
