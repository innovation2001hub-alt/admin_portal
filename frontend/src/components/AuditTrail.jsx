import React from 'react';

const AuditTrail = ({ logs }) => {
  const actionConfig = {
    CREATE: { icon: '✚', color: '#1f6feb', label: 'Created' },
    ASSIGN: { icon: '→', color: '#0969da', label: 'Assigned' },
    APPROVE: { icon: '✓', color: '#2cce7d', label: 'Approved' },
    REJECT: { icon: '✕', color: '#f64747', label: 'Rejected' },
    RESUBMIT: { icon: '↻', color: '#6e40aa', label: 'Resubmitted' },
    VIEW: { icon: '👁', color: '#8957e5', label: 'Viewed' },
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (!logs || logs.length === 0) {
    return <p style={{ color: '#666', fontStyle: 'italic' }}>No activity yet</p>;
  }

  return (
    <div className="audit-trail">
      {logs.map((log, index) => {
        const config = actionConfig[log.action] || { icon: '•', color: '#666', label: log.action };
        return (
          <div key={index} className="audit-trail-item">
            <div
              className="audit-trail-icon"
              style={{ backgroundColor: config.color }}
              title={config.label}
            >
              {config.icon}
            </div>
            <div className="audit-trail-content">
              <div className="audit-trail-action" style={{ color: config.color }}>
                <strong>{config.label}</strong>
                {log.performed_by && ` by ${log.performed_by.first_name || log.performed_by.username}`}
              </div>
              <div className="audit-trail-time">{formatDate(log.timestamp)}</div>
              {log.remarks && <div className="audit-trail-remarks">{log.remarks}</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AuditTrail;
