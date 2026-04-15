import React from 'react';

const containerStyles = {
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
  fontFamily: 'system-ui, Avenir, Helvetica, Arial, sans-serif',
  padding: '2rem',
  textAlign: 'center',
};

const cardStyles = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '20px',
  padding: '3rem 2.5rem',
  maxWidth: '480px',
  width: '100%',
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)',
};

const iconStyles = {
  fontSize: '64px',
  marginBottom: '1rem',
  display: 'block',
  animation: 'pulse 2.5s ease-in-out infinite',
};

const titleStyles = {
  fontFamily: "'Montserrat', system-ui, sans-serif",
  fontSize: '2.4rem',
  fontWeight: '700',
  background: 'linear-gradient(45deg, #4a6eb5, #7a54a8)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  margin: '0 0 0.5rem 0',
  letterSpacing: '1px',
};

const subtitleStyles = {
  fontSize: '1rem',
  color: 'rgba(255, 255, 255, 0.5)',
  margin: '0 0 2rem 0',
  letterSpacing: '3px',
  textTransform: 'uppercase',
  fontWeight: '400',
};

const messageStyles = {
  fontSize: '1.1rem',
  color: 'rgba(255, 255, 255, 0.8)',
  lineHeight: '1.7',
  margin: '0 0 2rem 0',
};

const dividerStyles = {
  width: '60px',
  height: '3px',
  background: 'linear-gradient(45deg, #4a6eb5, #7a54a8)',
  borderRadius: '2px',
  margin: '0 auto 2rem auto',
};

const tipStyles = {
  fontSize: '0.85rem',
  color: 'rgba(255, 255, 255, 0.35)',
  lineHeight: '1.6',
  margin: '0',
  borderTop: '1px solid rgba(255, 255, 255, 0.08)',
  paddingTop: '1.5rem',
};

const dotStyles = {
  display: 'inline-block',
  width: '8px',
  height: '8px',
  borderRadius: '50%',
  background: 'linear-gradient(45deg, #4a6eb5, #7a54a8)',
  margin: '0 3px',
  animation: 'bounce 1.4s ease-in-out infinite',
};

function MaintenancePage() {
  return (
    <>
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.08); opacity: 0.85; }
        }
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-6px); }
        }
      `}</style>
      <div style={containerStyles}>
        <div style={cardStyles}>
          <span style={iconStyles}>🛠️</span>
          <h1 style={titleStyles}>StudyAmigo</h1>
          <p style={subtitleStyles}>em manutenção</p>
          <div style={dividerStyles} />
          <p style={messageStyles}>
            Estamos realizando melhorias no sistema para tornar
            sua experiência de estudo ainda melhor.
            <br /><br />
            Voltamos em breve!
          </p>
          <div>
            <span style={{ ...dotStyles, animationDelay: '0s' }} />
            <span style={{ ...dotStyles, animationDelay: '0.2s' }} />
            <span style={{ ...dotStyles, animationDelay: '0.4s' }} />
          </div>
          <p style={tipStyles}>
            Enquanto isso, você pode continuar estudando pelo app Anki
            usando sua coleção exportada.
          </p>
        </div>
      </div>
    </>
  );
}

export default MaintenancePage;
