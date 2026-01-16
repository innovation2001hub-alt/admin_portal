import React from 'react';
import Dashboard from './Dashboard';

const MakerDashboard = () => {
  return <Dashboard roleTitle="Maker" color="#0065A4" highlights={["Create requests", "Track submissions", "Draft workflows"]} />;
};

export default MakerDashboard;
