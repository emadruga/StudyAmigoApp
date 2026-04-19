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
  const animals = [
    'Elefante', 'Cavalo', 'Golfinho', 'Tigre', 'Leao', 'Urso',
    'Pinguim', 'Macaco', 'Girafa', 'Zebra', 'Lobo', 'Raposa',
    'Gato', 'Cachorro', 'Coelho', 'Pato', 'Aguia', 'Cobra',
  ];
  const adjectives = [
    'Manco', 'Perneta', 'Alegre', 'Feliz', 'Doido', 'Valente',
    'Esperto', 'Rapido', 'Lento', 'Bravo', 'Manso', 'Gordo',
    'Magro', 'Alto', 'Baixo', 'Fofinho', 'Brioso', 'Teimoso',
  ];
  const separators = ['@', ':', '|'];

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const number = String(Math.floor(Math.random() * 900000) + 100000); // 6 dígitos
  const sep = pick(separators);

  return `${pick(animals)}${sep}${pick(adjectives)}${sep}${number}`;
}

const wrapperStyle = {
  position: 'relative',
  marginBottom: '10px',
};

const inputStyle = {
  display: 'block',
  width: 'calc(100% - 20px)',
  padding: '8px 36px 8px 8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
};

const eyeButtonStyle = {
  position: 'absolute',
  right: '24px',
  top: '50%',
  transform: 'translateY(-50%)',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  padding: '0',
  fontSize: '16px',
  color: '#666',
  lineHeight: 1,
};

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

// Campo de senha com ícone de olho para mostrar/ocultar
export function PasswordInput({ id, value, onChange, placeholder, minLength, maxLength, required }) {
  const [visible, setVisible] = useState(false);
  return (
    <div style={wrapperStyle}>
      <input
        type={visible ? 'text' : 'password'}
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        minLength={minLength}
        maxLength={maxLength}
        required={required}
        style={inputStyle}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        style={eyeButtonStyle}
        tabIndex={-1}
        aria-label={visible ? 'Ocultar senha' : 'Mostrar senha'}
      >
        {visible ? '🙈' : '👁️'}
      </button>
    </div>
  );
}

export default function PasswordStrengthRules({ password, onGenerate, onConfirm }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleGenerate = () => {
    const pwd = generatePassword();
    onGenerate(pwd);
    if (onConfirm) onConfirm(pwd);
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
