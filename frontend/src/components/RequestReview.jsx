import React, { useState, useEffect } from 'react';
import { approvalsAPI } from '../services/api';
import StatusBadge from './StatusBadge';
import ErrorAlert from './ErrorAlert';
import SuccessAlert from './SuccessAlert';
import AuditTrail from './AuditTrail';
import UnitHierarchy from './UnitHierarchy';

const RequestReview = ({ request, onClose, onApproveReject }) => {
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [actionType, setActionType] = useState('');

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const handleApprove = async () => {
    if (!remarks.trim()) {
      setError('Please add remarks before approving');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setActionType('approve');
      await approvalsAPI.approve(request.id, remarks);
      setSuccess('Request approved successfully!');
      setTimeout(() => {
        if (onApproveReject) onApproveReject();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.error || err.detail || 'Failed to approve request');
    } finally {
      setLoading(false);
      setActionType('');
    }
  };

  const handleReject = async () => {
    if (!remarks.trim()) {
      setError('Please add remarks before rejecting');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setActionType('reject');
      await approvalsAPI.reject(request.id, remarks);
      setSuccess('Request rejected successfully!');
      setTimeout(() => {
        if (onApproveReject) onApproveReject();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.error || err.detail || 'Failed to reject request');
    } finally {
      setLoading(false);
      setActionType('');
    }
  };

  return (
    <div className="review-modal">
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-content large">
        <div className="modal-header">
          <h3>Review Request #{request.id}</h3>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {error && <ErrorAlert message={error} onClose={() => setError('')} />}
          {success && <SuccessAlert message={success} onClose={() => setSuccess('')} />}

          <div className="review-section">
            <h4>Request Details</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="label">Request Type:</span>
                <span className="value">{request.request_type}</span>
              </div>
              <div className="detail-item">
                <span className="label">Status:</span>
                <span className="value">
                  <StatusBadge status={request.status} />
                </span>
              </div>
              <div className="detail-item">
                <span className="label">Title:</span>
                <span className="value">{request.title}</span>
              </div>
              <div className="detail-item">
                <span className="label">Requested:</span>
                <span className="value">{formatDate(request.created_at)}</span>
              </div>
            </div>
          </div>

          <div className="review-section">
            <h4>Maker Information</h4>
            <div className="detail-grid">
              <div className="detail-item">
                <span className="label">Name:</span>
                <span className="value">
                  {request.created_by?.first_name || request.created_by?.username}
                </span>
              </div>
              <div className="detail-item">
                <span className="label">Unit:</span>
                <div className="unit-info">
                  <UnitHierarchy unit={request.maker_unit} />
                </div>
              </div>
            </div>
          </div>

          <div className="review-section">
            <h4>Description</h4>
            <p className="description-text">{request.description}</p>
          </div>

          {request.payload && Object.keys(request.payload).length > 0 && (
            <div className="review-section">
              <h4>Request Data</h4>
              <pre className="payload-display">
                {JSON.stringify(request.payload, null, 2)}
              </pre>
            </div>
          )}

          {request.logs && request.logs.length > 0 && (
            <div className="review-section">
              <h4>Workflow History</h4>
              <AuditTrail logs={request.logs} />
            </div>
          )}

          <div className="review-section">
            <h4>Your Decision</h4>
            <div className="form-group">
              <label htmlFor="remarks">Remarks *</label>
              <textarea
                id="remarks"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Add your remarks about this request..."
                rows="4"
                disabled={loading}
                required
              />
              <small>Required. Explain your decision.</small>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn btn-secondary" disabled={loading}>
            Cancel
          </button>
          <button
            onClick={handleReject}
            className="btn btn-danger"
            disabled={loading || !remarks.trim()}
          >
            {actionType === 'reject' ? '⏳ Rejecting...' : '✕ Reject'}
          </button>
          <button
            onClick={handleApprove}
            className="btn btn-success"
            disabled={loading || !remarks.trim()}
          >
            {actionType === 'approve' ? '⏳ Approving...' : '✓ Approve'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RequestReview;
