import React, { useState, useEffect } from 'react';
import { approvalsAPI } from '../services/api';
import StatusBadge from './StatusBadge';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';
import AuditTrail from './AuditTrail';
import UnitHierarchy from './UnitHierarchy';

const AllRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    requestType: '',
  });

  useEffect(() => {
    fetchAllRequests();
  }, []);

  const fetchAllRequests = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await approvalsAPI.getAll();
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

  const filteredRequests = requests.filter((req) => {
    if (filters.status && req.status !== filters.status) return false;
    if (filters.requestType && req.request_type !== filters.requestType) return false;
    return true;
  });

  const requestTypes = [...new Set(requests.map((req) => req.request_type))];

  if (loading) return <LoadingSpinner text="Loading all requests..." />;

  return (
    <div className="list-card">
      <div className="list-header">
        <h2>All Requests (Admin View)</h2>
        <button onClick={fetchAllRequests} className="btn btn-secondary" disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      <div className="filter-bar admin-filters">
        <select
          value={filters.status}
          onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value }))}
          className="filter-select"
        >
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>

        <select
          value={filters.requestType}
          onChange={(e) => setFilters((prev) => ({ ...prev, requestType: e.target.value }))}
          className="filter-select"
        >
          <option value="">All Types</option>
          {requestTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>

        <p className="filter-info">
          Showing {filteredRequests.length} of {requests.length} requests
        </p>
      </div>

      {filteredRequests.length === 0 ? (
        <div className="empty-state">
          <p>No requests found matching the selected filters.</p>
        </div>
      ) : (
        <>
          <div className="requests-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Title</th>
                  <th>Maker</th>
                  <th>Status</th>
                  <th>Assigned To</th>
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
                    <td>{request.created_by?.first_name || request.created_by?.username}</td>
                    <td>
                      <StatusBadge status={request.status} />
                    </td>
                    <td>
                      {request.assigned_checker?.first_name ||
                        request.assigned_checker?.username ||
                        '-'}
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
              <div className="modal-content large">
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
                    <h4>Maker Information</h4>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <span className="label">Name:</span>
                        <span className="value">
                          {selectedRequest.created_by?.first_name ||
                            selectedRequest.created_by?.username}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Unit:</span>
                        <div className="unit-info">
                          <UnitHierarchy unit={selectedRequest.maker_unit} />
                        </div>
                      </div>
                    </div>
                  </div>

                  {selectedRequest.assigned_checker && (
                    <div className="detail-section">
                      <h4>Checker Assignment</h4>
                      <div className="detail-grid">
                        <div className="detail-item">
                          <span className="label">Assigned To:</span>
                          <span className="value">
                            {selectedRequest.assigned_checker.first_name ||
                              selectedRequest.assigned_checker.username}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="label">Checker Unit:</span>
                          <div className="unit-info">
                            <UnitHierarchy unit={selectedRequest.checker_unit} />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

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
                              ? selectedRequest.reviewed_by.first_name ||
                                selectedRequest.reviewed_by.username
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

export default AllRequests;
