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
  // [nome, gênero: 'm' | 'f']
  const animals = [
    ['Elefante', 'm'], ['Cavalo', 'm'], ['Golfinho', 'm'], ['Tigre', 'm'],
    ['Leao', 'm'],     ['Urso', 'm'],   ['Pinguim', 'm'], ['Macaco', 'm'],
    ['Lobo', 'm'],     ['Gato', 'm'],   ['Cachorro', 'm'], ['Coelho', 'm'],
    ['Pato', 'm'],     ['Cobra', 'f'],  ['Girafa', 'f'],  ['Zebra', 'f'],
    ['Raposa', 'f'],   ['Aguia', 'f'],
  ];

  // [forma masc, forma fem]
  const adjectives = [
    ['Manco', 'Manca'],       ['Alegre', 'Alegre'],
    ['Feliz', 'Feliz'],       ['Doido', 'Doida'],
    ['Valente', 'Valente'],   ['Esperto', 'Esperta'],
    ['Rapido', 'Rapida'],     ['Lento', 'Lenta'],
    ['Bravo', 'Brava'],       ['Manso', 'Mansa'],
    ['Gordo', 'Gorda'],       ['Magro', 'Magra'],
    ['Alto', 'Alta'],         ['Baixo', 'Baixa'],
    ['Fofinho', 'Fofinha'],   ['Brioso', 'Briosa'],
    ['Teimoso', 'Teimosa'],   ['Perneta', 'Perneta'],
  ];

  const separators = ['@', ':', '|'];

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  const [animalName, gender] = pick(animals);
  const adjPair = pick(adjectives);
  const adjective = gender === 'f' ? adjPair[1] : adjPair[0];
  const number = String(Math.floor(Math.random() * 900000) + 100000);
  const sep = pick(separators);

  // Número em posição aleatória: 0=início, 1=meio, 2=fim
  const pos = Math.floor(Math.random() * 3);
  const parts = pos === 0
    ? [number, animalName, adjective]
    : pos === 1
    ? [animalName, number, adjective]
    : [animalName, adjective, number];

  return parts.join(sep);
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
        {visible ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        )}
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
