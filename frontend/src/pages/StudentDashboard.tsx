import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LogOut, GraduationCap, MapPin, Calendar, Award, User,
  Briefcase, CheckCircle, XCircle, BookOpen, Building2,
  TrendingUp, Clock, AlertCircle, Loader2
} from 'lucide-react';
import api from '../services/api';
import './StudentDashboard.css';

interface StudentProfile {
  reg_number: string;
  name?: string;
  cgpa?: number;
  address?: string;
  age?: number;
  dob?: string;
  marks?: string;
  branch?: string;
  graduation_year?: number;
  active_backlogs?: boolean;
  placed?: boolean;
}

interface Job {
  id: number;
  company_name: string;
  job_role: string;
  description: string;
  tech_skills: string[];
  location: string;
  min_cgpa: number;
  backlogs?: boolean;
}

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'eligible'>('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, jobsRes] = await Promise.all([
          api.get('/users/me/profile'),
          api.get('/placements/jobs'),
        ]);
        setProfile(profileRes.data);
        setJobs(jobsRes.data);
      } catch (err: any) {
        console.error('Data fetch error', err);
        if (err?.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('role');
          navigate('/login');
        } else {
          setError('Failed to load dashboard data. Please try refreshing.');
        }
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

  const isEligible = (job: Job) => {
    if (!profile?.cgpa) return false;
    const cgpaOk = profile.cgpa >= job.min_cgpa;
    const backlogOk = job.backlogs === true || !profile.active_backlogs;
    return cgpaOk && backlogOk;
  };

  const displayedJobs = activeTab === 'eligible'
    ? jobs.filter(isEligible)
    : jobs;

  const eligibleCount = jobs.filter(isEligible).length;

  if (loading) {
    return (
      <div className="sd-loading">
        <Loader2 className="sd-spinner" size={40} />
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sd-loading">
        <AlertCircle size={40} color="#ef4444" />
        <p style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</p>
        <button className="sd-btn-primary" style={{ marginTop: '1rem' }} onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  const cgpaColor = (cgpa?: number) => {
    if (!cgpa) return '#64748b';
    if (cgpa >= 8.5) return '#10b981';
    if (cgpa >= 7.0) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="sd-root">
      {/* SIDEBAR */}
      <aside className="sd-sidebar">
        <div className="sd-sidebar-logo">
          <GraduationCap size={28} />
          <span>PlaceMe</span>
        </div>

        <div className="sd-avatar">
          <div className="sd-avatar-circle">
            {profile?.name ? profile.name[0].toUpperCase() : '?'}
          </div>
          <div className="sd-avatar-info">
            <p className="sd-avatar-name">{profile?.name || 'Student'}</p>
            <p className="sd-avatar-reg">{profile?.reg_number}</p>
          </div>
        </div>

        <nav className="sd-nav">
          <a className="sd-nav-item sd-nav-active" href="#">
            <Briefcase size={18} /> Opportunities
          </a>
          <a className="sd-nav-item" href="#profile-section">
            <User size={18} /> My Profile
          </a>
        </nav>

        <button className="sd-logout-btn" onClick={handleLogout}>
          <LogOut size={16} /> Logout
        </button>
      </aside>

      {/* MAIN CONTENT */}
      <main className="sd-main">

        {/* HEADER */}
        <header className="sd-header">
          <div>
            <h1 className="sd-header-title">Welcome back, {profile?.name?.split(' ')[0] || 'Student'}! 👋</h1>
            <p className="sd-header-sub">Track your placement journey and explore opportunities</p>
          </div>
        </header>

        {/* STATS ROW */}
        <div className="sd-stats-grid">
          <div className="sd-stat-card">
            <div className="sd-stat-icon" style={{ background: `${cgpaColor(profile?.cgpa)}20` }}>
              <Award size={22} style={{ color: cgpaColor(profile?.cgpa) }} />
            </div>
            <div>
              <p className="sd-stat-label">CGPA</p>
              <p className="sd-stat-value" style={{ color: cgpaColor(profile?.cgpa) }}>
                {profile?.cgpa ?? '—'}
              </p>
            </div>
          </div>

          <div className="sd-stat-card">
            <div className="sd-stat-icon" style={{ background: '#6366f120' }}>
              <BookOpen size={22} style={{ color: '#6366f1' }} />
            </div>
            <div>
              <p className="sd-stat-label">Branch</p>
              <p className="sd-stat-value">{profile?.branch ?? '—'}</p>
            </div>
          </div>

          <div className="sd-stat-card">
            <div className="sd-stat-icon" style={{ background: '#f59e0b20' }}>
              <Clock size={22} style={{ color: '#f59e0b' }} />
            </div>
            <div>
              <p className="sd-stat-label">Graduation</p>
              <p className="sd-stat-value">{profile?.graduation_year ?? '—'}</p>
            </div>
          </div>

          <div className="sd-stat-card">
            <div className="sd-stat-icon" style={{ background: '#10b98120' }}>
              <TrendingUp size={22} style={{ color: '#10b981' }} />
            </div>
            <div>
              <p className="sd-stat-label">Eligible For</p>
              <p className="sd-stat-value">{eligibleCount} Jobs</p>
            </div>
          </div>
        </div>

        {/* PROFILE SECTION */}
        <section className="sd-card" id="profile-section">
          <div className="sd-card-header">
            <User size={20} />
            <h2>My Profile</h2>
          </div>
          <div className="sd-profile-grid">
            <div className="sd-profile-field">
              <span className="sd-field-label"><User size={14} /> Full Name</span>
              <span className="sd-field-value">{profile?.name ?? 'Not available'}</span>
            </div>
            <div className="sd-profile-field">
              <span className="sd-field-label"><BookOpen size={14} /> Registration No.</span>
              <span className="sd-field-value">{profile?.reg_number}</span>
            </div>
            <div className="sd-profile-field">
              <span className="sd-field-label"><Calendar size={14} /> Date of Birth</span>
              <span className="sd-field-value">{profile?.dob ?? '—'}</span>
            </div>
            <div className="sd-profile-field">
              <span className="sd-field-label"><User size={14} /> Age</span>
              <span className="sd-field-value">{profile?.age ? `${profile.age} years` : '—'}</span>
            </div>
            <div className="sd-profile-field" style={{ gridColumn: '1 / -1' }}>
              <span className="sd-field-label"><MapPin size={14} /> Address</span>
              <span className="sd-field-value">{profile?.address ?? '—'}</span>
            </div>
            <div className="sd-profile-field">
              <span className="sd-field-label"><AlertCircle size={14} /> Active Backlogs</span>
              <span className="sd-field-value" style={{ color: profile?.active_backlogs ? '#ef4444' : '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                {profile?.active_backlogs
                  ? <><XCircle size={16} /> Yes</>
                  : <><CheckCircle size={16} /> No</>}
              </span>
            </div>
            <div className="sd-profile-field">
              <span className="sd-field-label"><TrendingUp size={14} /> Placement Status</span>
              <span className="sd-field-value" style={{ color: profile?.placed ? '#10b981' : '#f59e0b' }}>
                {profile?.placed ? '✅ Placed' : '🔍 Looking'}
              </span>
            </div>
          </div>
        </section>

        {/* JOB OPPORTUNITIES */}
        <section className="sd-card">
          <div className="sd-card-header">
            <Briefcase size={20} />
            <h2>Placement Opportunities</h2>
            <span className="sd-badge">{jobs.length} Total</span>
          </div>

          {/* Tab Filter */}
          <div className="sd-tabs">
            <button
              className={`sd-tab ${activeTab === 'all' ? 'sd-tab-active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              All Jobs ({jobs.length})
            </button>
            <button
              className={`sd-tab ${activeTab === 'eligible' ? 'sd-tab-active' : ''}`}
              onClick={() => setActiveTab('eligible')}
            >
              I'm Eligible ({eligibleCount})
            </button>
          </div>

          {displayedJobs.length === 0 ? (
            <div className="sd-empty">
              <Briefcase size={48} style={{ opacity: 0.3 }} />
              <p>{activeTab === 'eligible' ? 'No eligible jobs based on your profile.' : 'No opportunities posted yet. Check back soon!'}</p>
            </div>
          ) : (
            <div className="sd-jobs-grid">
              {displayedJobs.map((job) => {
                const eligible = isEligible(job);
                return (
                  <div key={job.id} className={`sd-job-card ${eligible ? 'sd-job-eligible' : 'sd-job-ineligible'}`}>
                    <div className="sd-job-header">
                      <div className="sd-company-badge">
                        <Building2 size={16} />
                        {job.company_name}
                      </div>
                      <span className={`sd-eligibility-badge ${eligible ? 'sd-eligible' : 'sd-not-eligible'}`}>
                        {eligible
                          ? <><CheckCircle size={12} /> Eligible</>
                          : <><XCircle size={12} /> Not Eligible</>}
                      </span>
                    </div>

                    <h3 className="sd-job-role">{job.job_role}</h3>
                    <p className="sd-job-desc">{job.description}</p>

                    <div className="sd-job-meta">
                      <span className="sd-meta-chip"><MapPin size={12} /> {job.location}</span>
                      <span className="sd-meta-chip"><Award size={12} /> Min {job.min_cgpa} CGPA</span>
                      {job.backlogs && <span className="sd-meta-chip" style={{ color: '#10b981' }}>Backlogs OK</span>}
                    </div>

                    <div className="sd-skills">
                      {Array.isArray(job.tech_skills) ? (
                        job.tech_skills.map((s) => (
                          <span key={s} className="sd-skill-tag">{s.trim()}</span>
                        ))
                      ) : (
                        typeof job.tech_skills === 'string' && (job.tech_skills as string).split(',').map((s) => (
                          <span key={s} className="sd-skill-tag">{s.trim()}</span>
                        ))
                      )}
                    </div>

                    {!eligible && (
                      <p className="sd-ineligible-reason">
                        {profile?.cgpa && profile.cgpa < job.min_cgpa
                          ? `Requires ${job.min_cgpa} CGPA (yours: ${profile.cgpa})`
                          : 'Backlogs not allowed for this role'}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default StudentDashboard;