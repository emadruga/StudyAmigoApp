import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api/axiosConfig.js';
import PasswordStrengthRules, { validatePassword, PasswordInput } from './PasswordStrengthRules.jsx';

const buttonStyle = {
  padding: '10px 20px',
  backgroundColor: '#4a6eb5',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
};
const errorStyle = { color: 'red', marginBottom: '10px' };
const successStyle = { color: 'green', marginBottom: '10px' };

const LANGUAGES = [
  { code: 'pt', flag: '🇧🇷' },
  { code: 'en', flag: '🇺🇸' },
  { code: 'es', flag: '🇪🇸' },
];

function FlagSelector() {
  const { i18n } = useTranslation();
  return (
    <span style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
      {LANGUAGES.map(({ code, flag }) => (
        <button
          key={code}
          type="button"
          onClick={() => i18n.changeLanguage(code)}
          title={code}
          style={{
            background: 'none',
            border: i18n.language === code ? '2px solid #4a6eb5' : '2px solid transparent',
            borderRadius: '4px',
            cursor: 'pointer',
            padding: '1px 3px',
            fontSize: '20px',
            lineHeight: 1,
            opacity: i18n.language === code ? 1 : 0.5,
          }}
        >
          {flag}
        </button>
      ))}
    </span>
  );
}

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
    if (!validatePassword(newPassword)) {
      setError(t('auth.errors.passwordComplexity'));
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h2 style={{ margin: 0 }}>{t('auth.resetPassword.title')}</h2>
        <FlagSelector />
      </div>
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
          <PasswordInput
            id="rp-new"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength="10"
            maxLength="20"
            required
            placeholder={t('auth.changePassword.newPlaceholder')}
          />
          <PasswordStrengthRules
            password={newPassword}
            onGenerate={(pwd) => setNewPassword(pwd)}
            onConfirm={(pwd) => setConfirmPassword(pwd)}
          />
          <label htmlFor="rp-confirm">{t('auth.confirmPassword')}</label>
          <PasswordInput
            id="rp-confirm"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
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
