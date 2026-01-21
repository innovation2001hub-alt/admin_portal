import React from 'react';

const ErrorAlert = ({ message, onClose }) => {
  return (
    <div
      style={{
        backgroundColor: '#ffebee',
        border: '1px solid #f64747',
        color: '#c1121f',
        padding: '12px 16px',
        borderRadius: '4px',
        marginBottom: '16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <div>
        <strong>Error:</strong> {message}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#f64747',
            cursor: 'pointer',
            fontSize: '20px',
            padding: '0',
            marginLeft: '16px',
          }}
        >
          ✕
        </button>
      )}
    </div>
  );
};

export default ErrorAlert;
