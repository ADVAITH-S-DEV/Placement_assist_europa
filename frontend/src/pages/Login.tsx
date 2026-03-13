import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { Building2, GraduationCap, Lock, Mail, ArrowRight } from 'lucide-react';
import api from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'student' | 'admin'>('student');
  const [error, setError] = useState('');
  
  // Admin Login State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // Student Registration State
  const [needsRegistration, setNeedsRegistration] = useState(false);
  const [googleToken, setGoogleToken] = useState('');
  const [regNumber, setRegNumber] = useState('');

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/admin/login', { email, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      navigate('/admin/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (tokenResponse: any) => {
    setError('');
    const token = tokenResponse.access_token;
    
    try {
      const response = await api.post('/auth/student/google', { token });
      // If successful without regNumber, they exist
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      navigate('/student/dashboard');
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Needs registration
        setGoogleToken(token);
        setNeedsRegistration(true);
      } else {
        setError(err.response?.data?.detail || 'Authentication failed');
      }
    }
  };

  const loginWithGoogle = useGoogleLogin({
    onSuccess: handleGoogleSuccess,
    onError: () => setError('Google Login Failed')
  });

  const handleStudentRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await api.post('/auth/student/google', { 
        token: googleToken, 
        reg_number: regNumber 
      });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      navigate('/student/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gradient auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Placement Assistance Portal</p>

        {/* Tab Toggle */}
        <div className="toggle-container">
          <button 
            className={`toggle-btn ${activeTab === 'student' ? 'active' : ''}`}
            onClick={() => { setActiveTab('student'); setError(''); setNeedsRegistration(false); }}
          >
            <GraduationCap className="inline-block w-4 h-4 mr-2" />
            Student
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => { setActiveTab('admin'); setError(''); }}
          >
            <Building2 className="inline-block w-4 h-4 mr-2" />
            Admin
          </button>
        </div>

        {error && <div className="error-msg mb-4">{error}</div>}

        {/* Student Content */}
        {activeTab === 'student' && !needsRegistration && (
          <div className="text-center">
            <button 
              onClick={() => loginWithGoogle()}
              className="btn btn-outline"
              style={{ padding: '0.75rem 1rem', display: 'flex', gap: '10px', alignItems: 'center', width: '100%', justifyContent: 'center' }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l3.68-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Sign in with Google
            </button>
            <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '1rem' }}>
              First time logging in? We will prompt you for your Registration Number to complete account setup.
            </p>
          </div>
        )}

        {/* Student Registration Form (if not found in DB) */}
        {activeTab === 'student' && needsRegistration && (
          <form onSubmit={handleStudentRegistration} className="animate-fade-in">
             <div className="form-group">
                <label className="form-label">Complete Registration</label>
                <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>
                  Please link your account to your university Registration Number to continue.
                </p>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Enter Registration Number (e.g., REG001)"
                  value={regNumber}
                  onChange={(e) => setRegNumber(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? 'Processing...' : 'Link Account'}
              </button>
          </form>
        )}

        {/* Admin Content */}
        {activeTab === 'admin' && (
          <form onSubmit={handleAdminLogin} className="animate-fade-in">
              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                   <Mail className="w-4 h-4 text-muted" /> Email Address
                </label>
                <input 
                  type="email" 
                  className="form-input" 
                  placeholder="admin@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                   <Lock className="w-4 h-4 text-muted" /> Password
                </label>
                <input 
                  type="password" 
                  className="form-input" 
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? 'Authenticating...' : 'Sign In as Admin'}
                {!loading && <ArrowRight className="inline-block w-4 h-4 ml-2" />}
              </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Login;
