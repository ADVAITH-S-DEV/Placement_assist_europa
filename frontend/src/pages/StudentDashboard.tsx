import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, GraduationCap, MapPin, Calendar, Award, User, Briefcase, CheckCircle } from 'lucide-react';
import api from '../services/api';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch profile and jobs in parallel
        const [profileRes, jobsRes] = await Promise.all([
          api.get('/users/me/profile'),
          api.get('/placements/jobs')
        ]);
        setProfile(profileRes.data);
        setJobs(jobsRes.data);
      } catch (err) {
        console.error("Data fetch error", err);
        // If profile fails, usually means session expired
        localStorage.removeItem('token');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  if (loading) return <div className="auth-container">Loading your dashboard...</div>;

  return (
    <div className="bg-gradient" style={{ minHeight: '100vh', padding: '2rem' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* PROFILE CARD */}
        <div style={{ background: 'var(--surface-color)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)', overflow: 'hidden' }}>
          <div style={{ padding: '1.5rem 2rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ padding: '0.75rem', background: 'var(--bg-color)', borderRadius: '50%' }}>
                <GraduationCap className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>Student Profile</h1>
                <p className="text-muted" style={{ margin: 0, fontSize: '0.875rem' }}>Reg. No: {profile?.reg_number}</p>
              </div>
            </div>
            <button onClick={handleLogout} className="btn btn-outline" style={{ width: 'auto', padding: '0.5rem 1rem' }}>
              <LogOut className="w-4 h-4 mr-2" /> Logout
            </button>
          </div>

          <div style={{ padding: '1.5rem 2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <User className="w-4 h-4 text-muted" /> Personal Details
              </h3>
              <p style={{ margin: 0 }}><strong>Age:</strong> {profile?.age} years</p>
              <p style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Calendar className="w-4 h-4" /> {profile?.dob}</p>
              <p style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}><MapPin className="w-4 h-4" /> {profile?.address}</p>
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Award className="w-4 h-4 text-muted" /> Performance
              </h3>
              <div style={{ background: 'var(--bg-color)', padding: '0.75rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-color)' }}>{profile?.cgpa}</span>
                <span style={{ fontSize: '0.875rem', marginLeft: '4px' }}>CGPA</span>
              </div>
            </div>
          </div>
        </div>

        {/* JOB LISTINGS SECTION */}
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Briefcase className="w-6 h-6" /> Available Opportunities
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {jobs.length === 0 ? (
              <p className="text-muted">No jobs posted yet.</p>
            ) : (
              jobs.map((job) => {
                const isEligible = profile?.cgpa >= job.min_cgpa;
                return (
                  <div key={job.id} style={{ 
                    background: 'var(--surface-color)', 
                    padding: '1.5rem', 
                    borderRadius: 'var(--radius-lg)', 
                    border: '1px solid var(--border-color)',
                    opacity: isEligible ? 1 : 0.7 
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.25rem 0.5rem', borderRadius: '4px', background: 'var(--bg-color)' }}>
                        {job.company_name}
                      </span>
                      {isEligible && (
                        <span style={{ color: '#10b981', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '2px' }}>
                          <CheckCircle className="w-3 h-3" /> Qualified
                        </span>
                      )}
                    </div>
                    
                    <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem' }}>{job.job_role}</h4>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem', height: '3rem', overflow: 'hidden' }}>
                      {job.description}
                    </p>
                    
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
                      {job.tech_skills.split(',').map((skill: string) => (
                        <span key={skill} style={{ fontSize: '0.7rem', background: 'var(--bg-color)', padding: '2px 6px', borderRadius: '4px' }}>
                          {skill.trim()}
                        </span>
                      ))}
                    </div>

                    <button 
                      className={isEligible ? "btn btn-primary" : "btn btn-outline"} 
                      style={{ width: '100%' }}
                      disabled={!isEligible}
                    >
                      {isEligible ? 'Apply Now' : `Requires ${job.min_cgpa} CGPA`}
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default StudentDashboard;