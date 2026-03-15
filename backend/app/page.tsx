export default function Home() {
  return (
    <div style={{
      backgroundColor: '#0a0a0a',
      color: '#00f2ff',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, sans-serif',
      textAlign: 'center'
    }}>
      <div style={{
        width: '150px',
        height: '150px',
        borderRadius: '50%',
        border: '4px solid #00f2ff',
        boxShadow: '0 0 20px #00f2ff, inset 0 0 20px #00f2ff',
        marginBottom: '2rem',
        animation: 'pulse 2s infinite ease-in-out'
      }}></div>
      <h1 style={{ fontSize: '3rem', margin: '0' }}>JARVIS</h1>
      <p style={{ color: '#888', fontSize: '1.2rem' }}>Systems are operational and cloud-synchronized.</p>
      
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); opacity: 0.8; }
          50% { transform: scale(1.05); opacity: 1; }
          100% { transform: scale(1); opacity: 0.8; }
        }
      `}</style>
    </div>
  );
}
