import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/axiosConfig.js';

const inputStyle = {
  display: 'block',
  width: 'calc(100% - 20px)',
  padding: '8px',
  marginBottom: '10px',
  border: '1px solid #ccc',
  borderRadius: '4px'
};
const buttonStyle = {
  padding: '10px 20px',
  backgroundColor: '#6c5ce7',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
};
const errorStyle = { color: 'red', marginBottom: '10px' };
const successStyle = { color: 'green', marginBottom: '10px' };

function ChangePasswordForm() {
  const { t } = useTranslation();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError(t('auth.errors.required'));
      return;
    }

    if (newPassword.length < 10 || newPassword.length > 20) {
      setError(t('auth.errors.passwordLength', { min: 10, max: 20 }));
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(t('auth.errors.passwordMatch'));
      return;
    }

    setLoading(true);
    try {
      await api.post('/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setSuccess(t('auth.changePassword.success'));
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError(t('auth.changePassword.failed'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{t('auth.changePassword.title')}</h2>
      {error && <p style={errorStyle}>{error}</p>}
      {success && <p style={successStyle}>{success}</p>}

      <label htmlFor="cp-current">{t('auth.changePassword.current')}</label>
      <input
        type="password"
        id="cp-current"
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
        required
        style={inputStyle}
        placeholder={t('auth.passwordPlaceholder')}
      />

      <label htmlFor="cp-new">{t('auth.passwordWithLimit', { min: 10, max: 20 })}</label>
      <input
        type="password"
        id="cp-new"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        minLength="10"
        maxLength="20"
        required
        style={inputStyle}
        placeholder={t('auth.changePassword.newPlaceholder')}
      />

      <label htmlFor="cp-confirm">{t('auth.confirmPassword')}</label>
      <input
        type="password"
        id="cp-confirm"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        style={inputStyle}
        placeholder={t('auth.confirmPasswordPlaceholder')}
      />

      <button type="submit" disabled={loading} style={buttonStyle}>
        {loading ? t('auth.changePassword.saving') : t('auth.changePassword.button')}
      </button>
    </form>
  );
}

export default ChangePasswordForm;
