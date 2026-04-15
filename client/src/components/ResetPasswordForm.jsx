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
  backgroundColor: '#4a6eb5',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
};
const linkStyle = {
  background: 'none',
  border: 'none',
  color: '#4a6eb5',
  cursor: 'pointer',
  fontSize: '13px',
  padding: 0,
  textDecoration: 'underline'
};
const errorStyle = { color: 'red', marginBottom: '10px' };
const successStyle = { color: 'green', marginBottom: '10px' };

function ResetPasswordForm({ token, onDone }) {
  const { t } = useTranslation();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!newPassword || !confirmPassword) {
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
      await api.post('/reset-password', { token, new_password: newPassword });
      setSuccess(t('auth.resetPassword.success'));
    } catch (err) {
      const msg = err.response?.data?.error;
      setError(msg || t('auth.resetPassword.failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{t('auth.resetPassword.title')}</h2>
      {error && <p style={errorStyle}>{error}</p>}
      {success ? (
        <>
          <p style={successStyle}>{success}</p>
          <button type="button" onClick={onDone} style={buttonStyle}>
            {t('auth.resetPassword.goToLogin')}
          </button>
        </>
      ) : (
        <>
          <label htmlFor="rp-new">{t('auth.passwordWithLimit', { min: 10, max: 20 })}</label>
          <input
            type="password"
            id="rp-new"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength="10"
            maxLength="20"
            required
            style={inputStyle}
            placeholder={t('auth.changePassword.newPlaceholder')}
          />
          <label htmlFor="rp-confirm">{t('auth.confirmPassword')}</label>
          <input
            type="password"
            id="rp-confirm"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            style={inputStyle}
            placeholder={t('auth.confirmPasswordPlaceholder')}
          />
          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? t('auth.resetPassword.saving') : t('auth.resetPassword.button')}
          </button>
        </>
      )}
    </form>
  );
}

export default ResetPasswordForm;
