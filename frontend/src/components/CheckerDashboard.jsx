import React from 'react';
import Dashboard from './Dashboard';

const CheckerDashboard = () => {
  return <Dashboard roleTitle="Checker" color="#738d9e" highlights={["Review approvals", "Validate data", "Sign-off items"]} />;
};

export default CheckerDashboard;
