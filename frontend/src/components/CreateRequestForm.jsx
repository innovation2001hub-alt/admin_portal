import React, { useState } from 'react';
import { approvalsAPI } from '../services/api';
import ErrorAlert from './ErrorAlert';
import SuccessAlert from './SuccessAlert';

const CreateRequestForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    requestType: '',
    title: '',
    description: '',
    payload: '{}',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const requestTypeOptions = [
    { value: 'CREATE_USER', label: 'Create New User' },
    { value: 'UPDATE_USER', label: 'Update User' },
    { value: 'DELETE_USER', label: 'Delete User' },
    { value: 'ASSIGN_ROLE', label: 'Assign Role' },
    { value: 'CHANGE_UNIT', label: 'Change Unit' },
    { value: 'DEACTIVATE_USER', label: 'Deactivate User' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate form
    if (!formData.requestType || !formData.title || !formData.description) {
      setError('Please fill in all required fields');
      return;
    }

    // Validate JSON payload
    let payloadObj = {};
    try {
      payloadObj = JSON.parse(formData.payload);
    } catch (e) {
      setError('Invalid JSON in payload field');
      return;
    }

    try {
      setLoading(true);
      const result = await approvalsAPI.create(
        formData.requestType,
        formData.title,
        formData.description,
        payloadObj
      );

      setSuccess(`Request created successfully! (ID: ${result.id})`);
      setFormData({
        requestType: '',
        title: '',
        description: '',
        payload: '{}',
      });

      if (onSuccess) {
        setTimeout(onSuccess, 1500);
      }
    } catch (err) {
      setError(err.error || err.detail || 'Failed to create request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card">
      <h2>Create New Request</h2>
      <p className="form-description">
        Submit a new request for approval. It will be automatically routed to the appropriate checker.
      </p>

      {error && <ErrorAlert message={error} onClose={() => setError('')} />}
      {success && <SuccessAlert message={success} onClose={() => setSuccess('')} />}

      <form onSubmit={handleSubmit} className="approval-form">
        <div className="form-group">
          <label htmlFor="requestType">Request Type *</label>
          <select
            id="requestType"
            name="requestType"
            value={formData.requestType}
            onChange={handleChange}
            disabled={loading}
            required
          >
            <option value="">Select request type...</option>
            {requestTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Brief summary of your request"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Detailed description of what you need"
            rows="4"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="payload">Payload (JSON)</label>
          <textarea
            id="payload"
            name="payload"
            value={formData.payload}
            onChange={handleChange}
            placeholder='{"key": "value"}'
            rows="3"
            disabled={loading}
          />
          <small>Optional: Additional data in JSON format</small>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Request'}
        </button>
      </form>
    </div>
  );
};

export default CreateRequestForm;
