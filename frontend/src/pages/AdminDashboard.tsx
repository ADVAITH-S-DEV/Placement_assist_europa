import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Users, Search } from 'lucide-react';
import api from '../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const res = await api.get('/users/students');
        setStudents(res.data);
      } catch (err) {
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchStudents();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg-color)' }}>
      {/* Navbar */}
      <nav style={{ background: 'var(--surface-color)', padding: '1rem 2rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'var(--primary-color)', padding: '0.5rem', borderRadius: 'var(--radius-md)', color: 'white' }}>
            <Users className="w-5 h-5" />
          </div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0 }}>Admin Portal</h1>
        </div>
        <button onClick={handleLogout} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto', padding: '0.5rem 1rem' }}>
          <LogOut className="w-4 h-4" /> Sign Out
        </button>
      </nav>

      {/* Main Content */}
      <main style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Registered Students</h2>
          <div style={{ position: 'relative' }}>
            <Search className="w-4 h-4 text-muted" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input 
              type="text" 
              placeholder="Search by name or reg no..." 
              className="form-input" 
              style={{ paddingLeft: '2.5rem', width: '300px' }}
              disabled
            />
          </div>
        </div>

        <div style={{ background: 'var(--surface-color)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading records...</div>
          ) : students.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>No students have registered yet.</div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Reg Number</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Name</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Google Account Email</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.reg_number} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>{student.reg_number}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-main)' }}>{student.name}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>{student.email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
