import React, { useState, useEffect } from 'react';
import { approvalsAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorAlert from './ErrorAlert';

const ApprovalMetrics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await approvalsAPI.getStatistics();
      setStats(data);
    } catch (err) {
      setError(err.error || 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading metrics..." />;

  const calculatePercentage = (value, total) => {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  };

  return (
    <div className="metrics-container">
      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      <div className="metrics-grid">
        <div className="metric-card total">
          <div className="metric-value">{stats?.total || 0}</div>
          <div className="metric-label">Total Requests</div>
        </div>

        <div className="metric-card pending">
          <div className="metric-value">{stats?.pending || 0}</div>
          <div className="metric-label">Pending</div>
          <div className="metric-percent">
            {calculatePercentage(stats?.pending, stats?.total)}%
          </div>
        </div>

        <div className="metric-card approved">
          <div className="metric-value">{stats?.approved || 0}</div>
          <div className="metric-label">Approved</div>
          <div className="metric-percent">
            {calculatePercentage(stats?.approved, stats?.total)}%
          </div>
        </div>

        <div className="metric-card rejected">
          <div className="metric-value">{stats?.rejected || 0}</div>
          <div className="metric-label">Rejected</div>
          <div className="metric-percent">
            {calculatePercentage(stats?.rejected, stats?.total)}%
          </div>
        </div>
      </div>

      {stats && (
        <div className="metrics-detail">
          <h3>Approval Statistics</h3>
          <div className="stats-bars">
            <div className="stat-bar-item">
              <label>Approval Rate</label>
              <div className="progress-bar">
                <div
                  className="progress-fill approved"
                  style={{
                    width: `${calculatePercentage(stats.approved, stats.approved + stats.rejected) || 0}%`,
                  }}
                />
              </div>
              <span className="stat-value">
                {stats.approved + stats.rejected > 0
                  ? calculatePercentage(stats.approved, stats.approved + stats.rejected)
                  : 0}
                %
              </span>
            </div>

            <div className="stat-bar-item">
              <label>Rejection Rate</label>
              <div className="progress-bar">
                <div
                  className="progress-fill rejected"
                  style={{
                    width: `${calculatePercentage(stats.rejected, stats.approved + stats.rejected) || 0}%`,
                  }}
                />
              </div>
              <span className="stat-value">
                {stats.approved + stats.rejected > 0
                  ? calculatePercentage(stats.rejected, stats.approved + stats.rejected)
                  : 0}
                %
              </span>
            </div>

            <div className="stat-bar-item">
              <label>Pending Rate</label>
              <div className="progress-bar">
                <div
                  className="progress-fill pending"
                  style={{
                    width: `${calculatePercentage(stats.pending, stats.total)}%`,
                  }}
                />
              </div>
              <span className="stat-value">
                {calculatePercentage(stats.pending, stats.total)}%
              </span>
            </div>
          </div>
        </div>
      )}

      <button onClick={fetchStatistics} className="btn btn-secondary" disabled={loading}>
        🔄 Refresh
      </button>
    </div>
  );
};

export default ApprovalMetrics;
