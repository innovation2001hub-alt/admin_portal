import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const getPrimaryRole = (user) => {
  if (!user || !Array.isArray(user.roles)) return null;
  if (user.roles.length === 0) return null;
  return user.roles[0]?.name || null;
};

const roleToPath = {
  ADMIN: '/admin/dashboard',
  MAKER: '/maker/dashboard',
  CHECKER: '/checker/dashboard',
};

const RoleRedirect = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const role = getPrimaryRole(user);
    const target = role ? roleToPath[role] : '/login';
    navigate(target, { replace: true });
  }, [user, navigate]);

  return null;
};

export default RoleRedirect;
