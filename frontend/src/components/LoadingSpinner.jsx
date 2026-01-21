import React from 'react';

const LoadingSpinner = ({ size = 'medium', text = 'Loading...' }) => {
  const sizeConfig = {
    small: { width: '24px', height: '24px', fontSize: '12px' },
    medium: { width: '40px', height: '40px', fontSize: '14px' },
    large: { width: '60px', height: '60px', fontSize: '16px' },
  };

  const style = sizeConfig[size] || sizeConfig.medium;

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <div
        style={{
          ...style,
          margin: '0 auto 10px',
          border: '3px solid #f3f3f3',
          borderTop: '3px solid #1f6feb',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <p style={{ color: '#666', fontSize: style.fontSize }}>{text}</p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
