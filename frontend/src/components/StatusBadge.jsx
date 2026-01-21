import React from 'react';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    PENDING: {
      color: '#FDB913',
      backgroundColor: '#fff8e1',
      label: 'Pending Approval',
    },
    APPROVED: {
      color: '#2cce7d',
      backgroundColor: '#e8f5e9',
      label: 'Approved',
    },
    REJECTED: {
      color: '#f64747',
      backgroundColor: '#ffebee',
      label: 'Rejected',
    },
  };

  const config = statusConfig[status] || statusConfig.PENDING;

  return (
    <span
      style={{
        color: config.color,
        backgroundColor: config.backgroundColor,
        padding: '6px 12px',
        borderRadius: '20px',
        fontSize: '12px',
        fontWeight: '600',
        border: `1px solid ${config.color}`,
        display: 'inline-block',
      }}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
