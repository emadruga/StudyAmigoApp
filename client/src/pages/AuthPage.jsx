import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LoginForm from '../components/LoginForm.jsx';
import ForgotPasswordForm from '../components/ForgotPasswordForm.jsx';
import ResetPasswordForm from '../components/ResetPasswordForm.jsx';

// Restore styles
const tabStyles = {
  padding: '10px 15px',
  cursor: 'pointer',
  border: '1px solid #ccc',
  borderBottom: 'none',
  marginRight: '5px',
  borderRadius: '5px 5px 0 0',
};
const activeTabStyles = {
  ...tabStyles,
  backgroundColor: '#eee',
  borderBottom: '1px solid #eee',
};
const inactiveTabStyles = {
  ...tabStyles,
  backgroundColor: '#f9f9f9',
};
const formContainerStyles = {
  border: '1px solid #ccc',
  padding: '20px',
  borderRadius: '0 5px 5px 5px',
  marginTop: '-1px' // Align border with tab bottom
};

// Add custom title styles
const titleStyles = {
  fontFamily: "'Montserrat', sans-serif",
  fontSize: '42px',
  fontWeight: '700',
  color: '#4a6eb5',
  textAlign: 'center',
  margin: '20px 0',
  textShadow: '2px 2px 4px rgba(0, 0, 0, 0.1)',
  letterSpacing: '1px',
  background: 'linear-gradient(45deg, #4a6eb5, #7a54a8)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  padding: '10px 0'
};

function AuthPage({ onLoginSuccess }) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('login');
  const [resetToken, setResetToken] = useState(null);

  // Detect ?reset_token=xxx in URL and switch to reset form
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('reset_token');
    if (token) {
      setResetToken(token);
      setActiveTab('resetPassword');
      // Clean token from URL without reloading
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const handleResetDone = () => {
    setResetToken(null);
    setActiveTab('login');
  };

  // While showing reset form, hide tabs entirely
  if (activeTab === 'resetPassword') {
    return (
      <div style={{ maxWidth: '400px', margin: '50px auto', fontFamily: 'Arial, sans-serif' }}>
        <h1 style={titleStyles}>{t('app.title')}</h1>
        <div style={formContainerStyles}>
          <ResetPasswordForm token={resetToken} onDone={handleResetDone} />
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={titleStyles}>{t('app.title')}</h1>
      <div>
        <button
          style={activeTab === 'login' ? activeTabStyles : inactiveTabStyles}
          onClick={() => setActiveTab('login')}
        >
          {t('auth.login')}
        </button>
        <button
          style={{ ...inactiveTabStyles, color: '#aaa', cursor: 'not-allowed' }}
          disabled
          title={t('auth.registerDisabledTooltip')}
        >
          {t('auth.register')}
        </button>
      </div>
      <div style={formContainerStyles}>
        {activeTab === 'login' && (
          <LoginForm
            onLoginSuccess={onLoginSuccess}
            onForgotPassword={() => setActiveTab('forgotPassword')}
          />
        )}
        {activeTab === 'forgotPassword' && (
          <ForgotPasswordForm onBack={() => setActiveTab('login')} />
        )}
      </div>
    </div>
  );
}

export default AuthPage;