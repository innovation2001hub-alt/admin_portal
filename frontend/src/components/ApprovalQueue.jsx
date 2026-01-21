import React, { useState, useEffect } from 'react';
import { approvalsAPI } from '../services/api';
import StatusBadge from './StatusBadge';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import UnitHierarchy from './UnitHierarchy';

const ApprovalQueue = ({ onSelectRequest }) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPendingQueue();
  }, []);

  const fetchPendingQueue = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await approvalsAPI.getPendingQueue();
      setRequests(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError(err.error || 'Failed to fetch pending requests');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (loading) return <LoadingSpinner text="Loading approval queue..." />;

  return (
    <div className="list-card">
      <div className="list-header">
        <h2>Pending Approvals</h2>
        <button onClick={fetchPendingQueue} className="btn btn-secondary" disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      <div className="queue-stats">
        <div className="stat-badge">
          <span className="stat-number">{requests.length}</span>
          <span className="stat-label">Pending Requests</span>
        </div>
      </div>

      {requests.length === 0 ? (
        <div className="empty-state">
          <p>No pending requests! You're all caught up. 🎉</p>
        </div>
      ) : (
        <div className="requests-grid">
          {requests.map((request) => (
            <div key={request.id} className="request-card">
              <div className="request-card-header">
                <h4>{request.title}</h4>
                <span className="request-id">#{request.id}</span>
              </div>

              <div className="request-card-body">
                <div className="request-detail">
                  <span className="label">Type:</span>
                  <span className="value">{request.request_type}</span>
                </div>

                <div className="request-detail">
                  <span className="label">Maker:</span>
                  <span className="value">
                    {request.created_by?.first_name || request.created_by?.username}
                  </span>
                </div>

                <div className="request-detail">
                  <span className="label">From Unit:</span>
                  <div className="unit-info">
                    <UnitHierarchy unit={request.maker_unit} />
                  </div>
                </div>

                <div className="request-detail">
                  <span className="label">Requested:</span>
                  <span className="value">{formatDate(request.created_at)}</span>
                </div>

                <p className="request-description">{request.description}</p>
              </div>

              <div className="request-card-footer">
                <button
                  onClick={() => onSelectRequest(request)}
                  className="btn btn-primary"
                >
                  Review & Approve
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ApprovalQueue;
