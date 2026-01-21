import React, { useState, useEffect } from 'react';
import { approvalsAPI } from '../services/api';
import StatusBadge from './StatusBadge';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import AuditTrail from './AuditTrail';
import UnitHierarchy from './UnitHierarchy';

const MyRequestsList = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await approvalsAPI.getMyRequests();
      setRequests(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError(err.error || 'Failed to fetch requests');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const filteredRequests = filterStatus
    ? requests.filter((req) => req.status === filterStatus)
    : requests;

  if (loading) return <LoadingSpinner text="Loading your requests..." />;

  return (
    <div className="list-card">
      <div className="list-header">
        <h2>My Requests</h2>
        <button onClick={fetchRequests} className="btn btn-secondary" disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      <div className="filter-bar">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="filter-select"
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>
        <p className="filter-info">
          Showing {filteredRequests.length} of {requests.length} requests
        </p>
      </div>

      {filteredRequests.length === 0 ? (
        <div className="empty-state">
          <p>No requests found. Start by creating a new request!</p>
        </div>
      ) : (
        <>
          <div className="requests-table">
            <table>
              <thead>
                <tr>
                  <th>Request ID</th>
                  <th>Type</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRequests.map((request) => (
                  <tr key={request.id}>
                    <td className="request-id">#{request.id}</td>
                    <td>{request.request_type}</td>
                    <td>{request.title}</td>
                    <td>
                      <StatusBadge status={request.status} />
                    </td>
                    <td>{formatDate(request.created_at)}</td>
                    <td>
                      <button
                        onClick={() => setSelectedRequest(request)}
                        className="btn btn-small btn-primary"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selectedRequest && (
            <div className="detail-modal">
              <div className="modal-overlay" onClick={() => setSelectedRequest(null)} />
              <div className="modal-content">
                <div className="modal-header">
                  <h3>Request Details (#{selectedRequest.id})</h3>
                  <button
                    onClick={() => setSelectedRequest(null)}
                    className="btn-close"
                  >
                    ✕
                  </button>
                </div>

                <div className="modal-body">
                  <div className="detail-section">
                    <h4>Request Information</h4>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <span className="label">Request Type:</span>
                        <span className="value">{selectedRequest.request_type}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Status:</span>
                        <span className="value">
                          <StatusBadge status={selectedRequest.status} />
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Title:</span>
                        <span className="value">{selectedRequest.title}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Created:</span>
                        <span className="value">{formatDate(selectedRequest.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="detail-section">
                    <h4>Description</h4>
                    <p>{selectedRequest.description}</p>
                  </div>

                  {selectedRequest.status !== 'PENDING' && (
                    <div className="detail-section">
                      <h4>Review Information</h4>
                      <div className="detail-grid">
                        <div className="detail-item">
                          <span className="label">Reviewed By:</span>
                          <span className="value">
                            {selectedRequest.reviewed_by
                              ? `${selectedRequest.reviewed_by.first_name || selectedRequest.reviewed_by.username}`
                              : 'N/A'}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Reviewed At:</span>
                          <span className="value">
                            {selectedRequest.reviewed_at
                              ? formatDate(selectedRequest.reviewed_at)
                              : 'N/A'}
                          </span>
                        </div>
                        {selectedRequest.remarks && (
                          <div className="detail-item full-width">
                            <span className="label">Remarks:</span>
                            <p className="remarks-text">{selectedRequest.remarks}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {selectedRequest.logs && selectedRequest.logs.length > 0 && (
                    <div className="detail-section">
                      <h4>Workflow History</h4>
                      <AuditTrail logs={selectedRequest.logs} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MyRequestsList;
