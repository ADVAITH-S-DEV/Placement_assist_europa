import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, GraduationCap, MapPin, Calendar, Award, User } from 'lucide-react';
import api from '../services/api';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/users/me/profile');
        setProfile(res.data);
      } catch (err) {
        // If unauthorized or token expired, force relogin
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  if (loading) {
    return <div className="auth-container">Loading your dashboard...</div>;
  }

  if (!profile) {
    return (
      <div className="auth-container" style={{ flexDirection: 'column' }}>
        <h2>No record found</h2>
        <button onClick={handleLogout} className="btn btn-outline mt-4">Return to Login</button>
      </div>
    );
  }

  return (
    <div className="bg-gradient" style={{ minHeight: '100vh', padding: '2rem' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', background: 'var(--surface-color)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)', overflow: 'hidden' }}>
        
        {/* Header */}
        <div style={{ padding: '2rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'var(--bg-color)', borderRadius: '50%' }}>
              <GraduationCap className="w-8 h-8 text-primary" style={{ color: 'var(--primary-color)' }} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>Student Profile</h1>
              <p className="text-muted" style={{ margin: 0 }}>Reg. No: {profile.reg_number}</p>
            </div>
          </div>
          <button onClick={handleLogout} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto' }}>
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: '2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <User className="w-5 h-5 text-muted" /> Personal Details
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}><strong className="text-muted">Age:</strong> {profile.age} years</div>
              <div style={{ display: 'flex', gap: '0.5rem' }}><Calendar className="w-4 h-4 text-muted" /> <strong className="text-muted">DOB:</strong> {profile.dob}</div>
              <div style={{ display: 'flex', gap: '0.5rem' }}><MapPin className="w-4 h-4 text-muted" /> <strong className="text-muted">Address:</strong> {profile.address}</div>
            </div>
          </div>

          <div>
             <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Award className="w-5 h-5 text-muted" /> Academic Performance
            </h3>
            <div style={{ background: 'var(--bg-color)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-color)', marginBottom: '0.5rem' }}>
                {profile.cgpa} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>CGPA</span>
              </div>
              <div>
                <strong className="text-muted">Detailed Marks:</strong>
                <p style={{ marginTop: '0.25rem', whiteSpace: 'pre-wrap' }}>{profile.marks}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default StudentDashboard;
