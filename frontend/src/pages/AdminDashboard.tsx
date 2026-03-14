import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Users, Search, PlusCircle, Calendar as CalendarIcon, Briefcase, X } from 'lucide-react';
import api from '../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [applicants, setApplicants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewAll, setViewAll] = useState(false); // false = eligible only, true = all applicants
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [newJob, setNewJob] = useState({
    company_name: '',
    job_role: '',
    description: '',
    tech_skills: '',
    location: '',
    min_cgpa: 0,
  });

  useEffect(() => {
    const fetchApplicants = async () => {
      setLoading(true);
      try {
        const endpoint = viewAll
          ? '/placements/applicants'
          : '/placements/eligible-applicants';
        const res = await api.get(endpoint);
        setApplicants(res.data);
      } catch (err) {
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchApplicants();
  }, [navigate, viewAll]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const handlePostJob = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const jobData = {
        ...newJob,
        tech_skills: newJob.tech_skills.split(',').map((s: string) => s.trim()),
        min_cgpa: Number(newJob.min_cgpa)
      };
      // Note: Endpoint updated to match our placements router
      await api.post('/placements/jobs', jobData);
      alert('Job posted and eligible students notified!');
      setIsJobModalOpen(false);
      // Reset form
      setNewJob({ company_name: '', job_role: '', description: '', tech_skills: '', location: '', min_cgpa: 0 });
    } catch (err) {
      console.error('Error posting job', err);
      alert('Failed to post job. Check console.');
    }
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
        
        {/* QUICK ACTIONS SECTION */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
          <div style={actionCardStyle}>
            <Briefcase className="w-8 h-8 text-primary" style={{ marginBottom: '1rem' }} />
            <h3 style={{ margin: '0.5rem 0' }}>Post New Job</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Broadcast opportunities to eligible students.</p>
            <button onClick={() => setIsJobModalOpen(true)} className="btn btn-primary" style={{ width: '100%' }}>
              <PlusCircle className="w-4 h-4 mr-2" /> Create Post
            </button>
          </div>

          <div style={actionCardStyle}>
            <Users className="w-8 h-8" style={{ marginBottom: '1rem', color: '#06b6d4' }} />
            <h3 style={{ margin: '0.5rem 0' }}>View Applications</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Review and manage student applications and resumes.</p>
            <button onClick={() => navigate('/admin/applications')} className="btn btn-outline" style={{ width: '100%' }}>
              Check Applications
            </button>
          </div>

          <div style={actionCardStyle}>
            <CalendarIcon className="w-8 h-8" style={{ marginBottom: '1rem', color: '#8b5cf6' }} />
            <h3 style={{ margin: '0.5rem 0' }}>Manage Schedule</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Set interview rounds and calendar events.</p>
            <button onClick={() => navigate('/admin/calendar')} className="btn btn-outline" style={{ width: '100%' }}>
              View Calendar
            </button>
          </div>
        </div>

        {/* APPLICANTS TABLE SECTION */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>
            {viewAll ? 'All Applicants' : 'Eligible Applicants'}
          </h2>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <Search className="w-4 h-4 text-muted" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                type="text" 
                placeholder="Search by name or reg no..." 
                className="form-input" 
                style={{ paddingLeft: '2.5rem', width: '260px' }}
              />
            </div>
            <button
              className="btn btn-outline"
              style={{ width: 'auto' }}
              onClick={() => setViewAll(!viewAll)}
            >
              {viewAll ? 'View Eligible Only' : 'View All Applicants'}
            </button>
          </div>
        </div>

        <div style={{ background: 'var(--surface-color)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading records...</div>
          ) : applicants.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              {viewAll ? 'No applicants found.' : 'No eligible applicants found.'}
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Reg. No</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Name</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Branch</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Grad. Year</th>
                  <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Placed?</th>
                  {!viewAll && (
                    <>
                      <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Opportunity</th>
                      <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Interview Status</th>
                      <th style={{ padding: '1rem 1.5rem', fontWeight: 500, color: 'var(--text-muted)' }}>Actions</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {applicants.map((app) => (
                  <tr key={app.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>{app.reg_number}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>{app.name}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>{app.branch || '—'}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>{app.graduation_year || '—'}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>{app.placed ? 'Placed' : 'Not placed'}</td>
                    {!viewAll && (
                      <>
                        <td style={{ padding: '1rem 1.5rem' }}>
                          {app.job_role} at {app.company_name}
                        </td>
                        <td style={{ padding: '1rem 1.5rem' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                            <span>
                              {app.is_completed
                                ? 'Completed'
                                : app.is_scheduled
                                ? 'Scheduled'
                                : 'Not scheduled'}
                            </span>
                            {app.interview_start && (
                              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                {new Date(app.interview_start).toLocaleString()}
                              </span>
                            )}
                          </div>
                        </td>
                        <td style={{ padding: '1rem 1.5rem' }}>
                          <button
                            className="btn btn-outline"
                            onClick={() => navigate(`/admin/calendar?studentId=${app.id}&jobId=${app.job_id}`)}
                          >
                            Schedule Interview
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>

      {/* JOB POSTING MODAL */}
      {isJobModalOpen && (
        <div style={overlayStyle}>
          <div style={modalStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ margin: 0 }}>Post New Opportunity</h2>
              <X className="w-6 h-6 cursor-pointer" onClick={() => setIsJobModalOpen(false)} />
            </div>
            <form onSubmit={handlePostJob} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <input 
                placeholder="Company Name" required style={inputStyle}
                value={newJob.company_name} onChange={e => setNewJob({...newJob, company_name: e.target.value})} 
              />
              <input 
                placeholder="Job Role" required style={inputStyle}
                value={newJob.job_role} onChange={e => setNewJob({...newJob, job_role: e.target.value})} 
              />
              <div style={{ display: 'flex', gap: '1rem' }}>
                <input 
                  placeholder="Location" required style={{...inputStyle, flex: 1}}
                  value={newJob.location} onChange={e => setNewJob({...newJob, location: e.target.value})} 
                />
                <input 
                  type="number" step="0.1" placeholder="Min CGPA" required style={{...inputStyle, width: '120px'}}
                  value={newJob.min_cgpa} onChange={e => setNewJob({...newJob, min_cgpa: Number(e.target.value)})} 
                />
              </div>
              <input 
                placeholder="Tech Skills (comma separated: React, Python)" required style={inputStyle}
                value={newJob.tech_skills} onChange={e => setNewJob({...newJob, tech_skills: e.target.value})} 
              />
              <textarea 
                placeholder="Job Description" rows={4} style={inputStyle}
                value={newJob.description} onChange={e => setNewJob({...newJob, description: e.target.value})} 
              />
              <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem', marginTop: '1rem' }}>
                Publish & Notify Students
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Inline Styles
const actionCardStyle = {
  background: 'var(--surface-color)',
  padding: '1.5rem',
  borderRadius: 'var(--radius-lg)',
  border: '1px solid var(--border-color)',
  display: 'flex',
  flexDirection: 'column' as const,
  alignItems: 'center',
  textAlign: 'center' as const,
};

const overlayStyle = {
  position: 'fixed' as const,
  top: 0, left: 0, width: '100%', height: '100%',
  background: 'rgba(0,0,0,0.5)',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  zIndex: 1000,
};

const modalStyle = {
  background: 'var(--surface-color)',
  padding: '2rem',
  borderRadius: 'var(--radius-lg)',
  width: '90%',
  maxWidth: '500px',
  boxShadow: 'var(--shadow-lg)',
};

const inputStyle = {
  padding: '0.75rem',
  borderRadius: 'var(--radius-md)',
  border: '1px solid var(--border-color)',
  background: 'var(--bg-color)',
  fontSize: '0.875rem',
};

export default AdminDashboard;