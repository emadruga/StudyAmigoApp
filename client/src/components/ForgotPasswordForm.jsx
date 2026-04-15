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

function ForgotPasswordForm({ onBack }) {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!email) {
      setError(t('auth.errors.required'));
      return;
    }
    setLoading(true);
    try {
      await api.post('/request-password-reset', { email });
      setSuccess(t('auth.forgotPassword.sent'));
    } catch (err) {
      // Server always returns 200 — only network errors reach here
      setError(t('auth.forgotPassword.failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{t('auth.forgotPassword.title')}</h2>
      <p style={{ color: '#555', fontSize: '14px', marginBottom: '12px' }}>
        {t('auth.forgotPassword.instructions')}
      </p>
      {error && <p style={errorStyle}>{error}</p>}
      {success && <p style={successStyle}>{success}</p>}
      {!success && (
        <>
          <label htmlFor="forgot-email">{t('auth.email')}</label>
          <input
            type="email"
            id="forgot-email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={inputStyle}
            placeholder={t('auth.emailPlaceholder')}
          />
          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? t('auth.forgotPassword.sending') : t('auth.forgotPassword.button')}
          </button>
        </>
      )}
      <div style={{ marginTop: '16px' }}>
        <button type="button" onClick={onBack} style={linkStyle}>
          ← {t('auth.forgotPassword.backToLogin')}
        </button>
      </div>
    </form>
  );
}

export default ForgotPasswordForm;
