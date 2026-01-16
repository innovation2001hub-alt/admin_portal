import React from 'react';
import Dashboard from './Dashboard';

const CheckerDashboard = () => {
  return <Dashboard roleTitle="Checker" color="#0065A4" highlights={["Review approvals", "Validate data", "Sign-off items"]} />;
};

export default CheckerDashboard;
