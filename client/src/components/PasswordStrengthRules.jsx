import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export const PASSWORD_RULES = [
  { key: 'minLength',  test: (p) => p.length >= 10 },
  { key: 'uppercase',  test: (p) => /[A-Z]/.test(p) },
  { key: 'lowercase',  test: (p) => /[a-z]/.test(p) },
  { key: 'number',     test: (p) => /[0-9]/.test(p) },
  { key: 'special',    test: (p) => /[^A-Za-z0-9]/.test(p) },
];

export function validatePassword(password) {
  return PASSWORD_RULES.every(({ test }) => test(password));
}

function generatePassword() {
  const upper   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lower   = 'abcdefghijklmnopqrstuvwxyz';
  const digits  = '0123456789';
  const special = '!@#$%&*?';
  const all     = upper + lower + digits + special;

  // Guarantee at least one of each required class
  const pick = (src) => src[Math.floor(Math.random() * src.length)];
  const required = [pick(upper), pick(lower), pick(digits), pick(special)];

  const remaining = Array.from({ length: 8 }, () => pick(all));
  const combined  = [...required, ...remaining];

  // Fisher-Yates shuffle
  for (let i = combined.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [combined[i], combined[j]] = [combined[j], combined[i]];
  }
  return combined.join('');
}

const ruleListStyle = {
  listStyle: 'none',
  padding: 0,
  margin: '4px 0 12px 0',
  fontSize: '12px',
};

const generateRowStyle = {
  display: 'flex',
  gap: '8px',
  marginBottom: '10px',
  alignItems: 'center',
};

const smallButtonStyle = (color) => ({
  padding: '5px 10px',
  backgroundColor: color,
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '12px',
  whiteSpace: 'nowrap',
});

export default function PasswordStrengthRules({ password, onGenerate }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleGenerate = () => {
    const pwd = generatePassword();
    onGenerate(pwd);
    setCopied(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(password).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div>
      <div style={generateRowStyle}>
        <button type="button" onClick={handleGenerate} style={smallButtonStyle('#2d8a4e')}>
          {t('auth.passwordHelper.generate')}
        </button>
        {password && (
          <button type="button" onClick={handleCopy} style={smallButtonStyle(copied ? '#888' : '#4a6eb5')}>
            {copied ? t('auth.passwordHelper.copied') : t('auth.passwordHelper.copy')}
          </button>
        )}
      </div>
      <ul style={ruleListStyle}>
        {PASSWORD_RULES.map(({ key, test }) => {
          const ok = test(password);
          return (
            <li key={key} style={{ color: ok ? '#2d8a4e' : '#888' }}>
              {ok ? '✓' : '○'} {t(`auth.passwordHelper.rules.${key}`)}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
