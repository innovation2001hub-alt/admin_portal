import React from 'react';

const SuccessAlert = ({ message, onClose }) => {
  return (
    <div
      style={{
        backgroundColor: '#e8f5e9',
        border: '1px solid #2cce7d',
        color: '#1b7236',
        padding: '12px 16px',
        borderRadius: '4px',
        marginBottom: '16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <div>
        <strong>Success!</strong> {message}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: '#2cce7d',
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

export default SuccessAlert;
