import React, { useState, useEffect } from 'react';
import '../styles/UserManagement.css';

const UserManagement = ({ token }) => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form states
  const [formMode, setFormMode] = useState('list'); // 'list', 'create', 'edit'
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    employee_id: '',
    unit_id: '',
    role_ids: [],
    is_active: true,
  });

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Check if token is available
  if (!token) {
    return (
      <div className="user-management">
        <div className="alert alert-error">
          Authentication token not found. Please log in again.
        </div>
      </div>
    );
  }

  // Load data on mount
  useEffect(() => {
    if (token) {
      fetchUsers();
      fetchRoles();
      fetchUnits();
    }
  }, [token]);

  // Fetch users
  const fetchUsers = async (pageNum = 1) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/user-management/?page=${pageNum}&page_size=${pageSize}`,
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setUsers(data.results || data);
        setTotalCount(data.count || data.length);
        setPage(pageNum);
        setError('');
      } else {
        setError('Failed to fetch users');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch available roles
  const fetchRoles = async () => {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/user-management/available-roles/',
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setRoles(data);
      }
    } catch (err) {
      console.error('Error fetching roles:', err);
    }
  };

  // Fetch available units
  const fetchUnits = async () => {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/user-management/available-units/',
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setUnits(data);
      }
    } catch (err) {
      console.error('Error fetching units:', err);
    }
  };

  // Create user
  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/user-management/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          is_active: formData.is_active,
        })
      });

      if (response.ok) {
        setSuccess('User created successfully!');
        setFormMode('list');
        setFormData({
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          employee_id: '',
          unit_id: '',
          role_ids: [],
          is_active: true,
        });
        fetchUsers(1);
      } else {
        const errData = await response.json();
        setError(`Error: ${JSON.stringify(errData)}`);
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Update user
  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/user-management/${selectedUser.id}/`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            first_name: formData.first_name,
            last_name: formData.last_name,
            employee_id: formData.employee_id,
            unit_id: formData.unit_id,
            role_ids: formData.role_ids,
            is_active: formData.is_active,
          })
        }
      );

      if (response.ok) {
        setSuccess('User updated successfully!');
        setFormMode('list');
        fetchUsers(page);
      } else {
        const errData = await response.json();
        setError(`Error: ${JSON.stringify(errData)}`);
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Delete user
  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;

    setLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/user-management/${userId}/`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Token ${token}` }
        }
      );

      if (response.ok) {
        setSuccess('User deleted successfully!');
        fetchUsers(page);
      } else {
        setError('Failed to delete user');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset password
  const handleResetPassword = async (userId) => {
    const newPassword = prompt('Enter new password:');
    if (!newPassword) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/user-management/${userId}/reset-password/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ password: newPassword })
        }
      );

      if (response.ok) {
        setSuccess('Password reset successfully!');
      } else {
        setError('Failed to reset password');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    }
  };

  // Edit user
  const handleEdit = (user) => {
    setSelectedUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      employee_id: user.employee_id,
      unit_id: user.unit_display?.id || '',
      role_ids: user.roles.map(r => r.id || r),
      is_active: user.is_active,
    });
    setFormMode('edit');
  };

  // New user form
  const handleNewUser = () => {
    setSelectedUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      employee_id: '',
      unit_id: '',
      role_ids: [],
      is_active: true,
    });
    setFormMode('create');
  };

  // Render list view
  if (formMode === 'list') {
    return (
      <div className="user-management">
        <h2>User Management</h2>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="controls">
          <button onClick={handleNewUser} className="btn btn-primary">
            + Create New User
          </button>
        </div>

        {loading ? (
          <p>Loading users...</p>
        ) : (
          <>
            <div className="users-table">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Unit</th>
                    <th>Roles</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id} className={!user.is_active ? 'inactive' : ''}>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.first_name} {user.last_name}</td>
                      <td>{user.unit_display ? user.unit_display.name : 'N/A'}</td>
                      <td>{user.roles.join(', ')}</td>
                      <td>
                        <span className={`badge ${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="actions">
                        <button
                          onClick={() => handleEdit(user)}
                          className="btn btn-sm btn-edit"
                          title="Edit"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleResetPassword(user.id)}
                          className="btn btn-sm btn-warning"
                          title="Reset Password"
                        >
                          Reset PW
                        </button>
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="btn btn-sm btn-danger"
                          title="Delete"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <button
                onClick={() => fetchUsers(page - 1)}
                disabled={page === 1}
                className="btn btn-sm"
              >
                Previous
              </button>
              <span>Page {page} of {Math.ceil(totalCount / pageSize)}</span>
              <button
                onClick={() => fetchUsers(page + 1)}
                disabled={page >= Math.ceil(totalCount / pageSize)}
                className="btn btn-sm"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  // Render form (create/edit)
  return (
    <div className="user-management">
      <h2>{formMode === 'create' ? 'Create New User' : 'Edit User'}</h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <form onSubmit={formMode === 'create' ? handleCreate : handleUpdate} className="user-form">
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            disabled={formMode === 'edit'}
            required
          />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>

        <div className="form-group">
          <label>First Name</label>
          <input
            type="text"
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Last Name</label>
          <input
            type="text"
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Employee ID</label>
          <input
            type="text"
            value={formData.employee_id}
            onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
          />
        </div>

        {formMode === 'create' && (
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
        )}

        <div className="form-group">
          <label>Unit</label>
          <select
            value={formData.unit_id}
            onChange={(e) => setFormData({ ...formData, unit_id: e.target.value })}
          >
            <option value="">-- Select Unit --</option>
            {units.map(unit => (
              <option key={unit.id} value={unit.id}>
                {unit.name} ({unit.unit_type})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Roles</label>
          <div className="roles-list">
            {roles.map(role => (
              <div key={role.id} className="role-checkbox">
                <input
                  type="checkbox"
                  id={`role-${role.id}`}
                  checked={formData.role_ids.includes(role.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setFormData({
                        ...formData,
                        role_ids: [...formData.role_ids, role.id]
                      });
                    } else {
                      setFormData({
                        ...formData,
                        role_ids: formData.role_ids.filter(id => id !== role.id)
                      });
                    }
                  }}
                />
                <label htmlFor={`role-${role.id}`}>
                  {role.name} - {role.description}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            />
            Active
          </label>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Saving...' : formMode === 'create' ? 'Create User' : 'Update User'}
          </button>
          <button
            type="button"
            onClick={() => setFormMode('list')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserManagement;
