import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LogOut, GraduationCap, MapPin, Calendar, Award, User,
  Briefcase, CheckCircle, XCircle, BookOpen, Building2,
  TrendingUp, Clock, AlertCircle, Loader2, Send, X, Upload,
  FileText, Sparkles, Download, BarChart3, WandSparkles, ExternalLink
} from 'lucide-react';
import axios from 'axios';
import api from '../services/api';
import './StudentDashboard.css';

interface StudentProfile {
  id?: number;
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

interface ApplicationStatus {
  [jobId: number]: {
    applied: boolean;
    status: string;
    id: number;
  };
}

interface ApplicationForm {
  resume: File | null;
  coverLetter: string;
}

interface AtsResult {
  score: number | null;
  summary: string;
  matchedKeywords: string[];
  missingKeywords: string[];
}

interface EnhancementResult {
  originalScore: number | null;
  enhancedScore: number | null;
  pdfUrl: string | null;
}

const NODE_API_BASE_URL = 'http://localhost:5000';
const AI_API_BASE_URL = import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001';

const collectStringValues = (value: unknown): string[] => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? [trimmed] : [];
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => collectStringValues(item));
  }

  if (value && typeof value === 'object') {
    return Object.values(value).flatMap((item) => collectStringValues(item));
  }

  return [];
};

const normalizeLabel = (value: string) =>
  value
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());

const flattenKeyValueText = (value: unknown): string[] => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? [trimmed] : [];
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return [String(value)];
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => flattenKeyValueText(item));
  }

  if (value && typeof value === 'object') {
    return Object.entries(value).flatMap(([key, nestedValue]) => {
      if (
        nestedValue &&
        typeof nestedValue === 'object' &&
        !Array.isArray(nestedValue)
      ) {
        return flattenKeyValueText(nestedValue).map(
          (entry) => `${normalizeLabel(key)}: ${entry}`
        );
      }

      const normalizedValue = flattenKeyValueText(nestedValue).join(', ');
      return normalizedValue ? [`${normalizeLabel(key)}: ${normalizedValue}`] : [];
    });
  }

  return [];
};

const collectKeywordValues = (payload: any, keys: string[]) => {
  const seen = new Set<string>();
  const values: string[] = [];

  const visit = (node: any) => {
    if (!node || typeof node !== 'object') return;

    if (Array.isArray(node)) {
      node.forEach(visit);
      return;
    }

    Object.entries(node).forEach(([key, value]) => {
      const normalizedKey = key.toLowerCase();
      if (keys.some((candidate) => normalizedKey.includes(candidate))) {
        flattenKeyValueText(value).forEach((entry) => {
          if (!seen.has(entry)) {
            seen.add(entry);
            values.push(entry);
          }
        });
      }

      if (value && typeof value === 'object') {
        visit(value);
      }
    });
  };

  visit(payload);
  return values;
};

const tryParseJsonString = (value: unknown) => {
  if (typeof value !== 'string') return null;

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

const extractSuggestions = (analysisPayload: any): string[] => {
  const explicitError =
    analysisPayload?.error?.message ||
    analysisPayload?.detail ||
    analysisPayload?.message;

  if (explicitError) {
    const failedGeneration = analysisPayload?.error?.failed_generation;
    const parsedFailedGeneration = tryParseJsonString(failedGeneration);
    const recoveredSuggestions = parsedFailedGeneration
      ? collectStringValues(
          parsedFailedGeneration?.suggestions ||
          parsedFailedGeneration?.top_3_missing_skills ||
          parsedFailedGeneration?.action_result_rewrites
        )
      : [];
    const errorLines = [explicitError];

    if (recoveredSuggestions.length > 0) {
      errorLines.push(...recoveredSuggestions);
    } else if (failedGeneration) {
      errorLines.push('Model output could not be validated. Showing raw details below.');
      errorLines.push(...flattenKeyValueText(failedGeneration));
    }

    return errorLines;
  }

  const candidates = [
    analysisPayload?.suggestions,
    analysisPayload?.recommendations,
    analysisPayload?.feedback,
    analysisPayload?.improvements,
    analysisPayload?.analysis,
    analysisPayload,
  ];

  const unique = Array.from(
    new Set(candidates.flatMap((candidate) => collectStringValues(candidate)))
  );

  return unique.slice(0, 8);
};

const parseScore = (scorePayload: any): AtsResult => {
  const scoreCandidates = [
    scorePayload?.score,
    scorePayload?.ats_score,
    scorePayload?.match_score,
    scorePayload?.data?.score,
    scorePayload?.data?.ats_score,
    scorePayload?.data?.match_score,
  ];

  const numericScore = scoreCandidates.find((value) => typeof value === 'number');
  const matchedKeywords = collectKeywordValues(scorePayload, ['matched', 'present', 'overlap', 'aligned']);
  const missingKeywords = collectKeywordValues(scorePayload, ['missing', 'gap', 'absent', 'lacking']);

  return {
    score: numericScore ?? null,
    summary:
      scorePayload?.summary ||
      scorePayload?.message ||
      scorePayload?.data?.summary ||
      'ATS analysis completed.',
    matchedKeywords: matchedKeywords.slice(0, 12),
    missingKeywords: missingKeywords.slice(0, 12),
  };
};

const buildPdfUrl = (pdfPath: string | null) => {
  if (!pdfPath) return null;
  if (pdfPath.startsWith('http://') || pdfPath.startsWith('https://')) {
    return pdfPath;
  }
  return `${AI_API_BASE_URL}${pdfPath}`;
};

const StudentDashboard = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const resumeEnhancerInputRef = useRef<HTMLInputElement>(null);
  const [activeSection, setActiveSection] = useState<'opportunities' | 'profile' | 'resume-enhancer'>('opportunities');
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [selectedJobForApplication, setSelectedJobForApplication] = useState<Job | null>(null);
  const [applicationForm, setApplicationForm] = useState<ApplicationForm>({
    resume: null,
    coverLetter: ''
  });
  const [submittingApplication, setSubmittingApplication] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'eligible'>('all');
  const [applications, setApplications] = useState<ApplicationStatus>({});
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumePreviewUrl, setResumePreviewUrl] = useState<string | null>(null);
  const [resumeUploadMessage, setResumeUploadMessage] = useState<string>('');
  const [jobDescription, setJobDescription] = useState('');
  const [resumeJson, setResumeJson] = useState<any>(null);
  const [atsResult, setAtsResult] = useState<AtsResult | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [enhancementResult, setEnhancementResult] = useState<EnhancementResult | null>(null);
  const [enhancedResumePreviewUrl, setEnhancedResumePreviewUrl] = useState<string | null>(null);
  const [analyzingResume, setAnalyzingResume] = useState(false);
  const [enhancingResume, setEnhancingResume] = useState(false);
  const [resumeEnhancerError, setResumeEnhancerError] = useState<string | null>(null);

  useEffect(() => {
    if (!resumeFile) {
      setResumePreviewUrl(null);
      return;
    }

    const nextPreviewUrl = URL.createObjectURL(resumeFile);
    setResumePreviewUrl(nextPreviewUrl);

    return () => {
      URL.revokeObjectURL(nextPreviewUrl);
    };
  }, [resumeFile]);

  useEffect(() => {
    if (!enhancementResult?.pdfUrl) {
      setEnhancedResumePreviewUrl(null);
      return;
    }

    let isActive = true;
    let objectUrl: string | null = null;

    const loadPreview = async () => {
      try {
        const response = await axios.get(enhancementResult.pdfUrl!, {
          responseType: 'blob',
        });

        objectUrl = URL.createObjectURL(response.data);
        if (isActive) {
          setEnhancedResumePreviewUrl(objectUrl);
        }
      } catch (error) {
        console.error('Enhanced resume preview failed', error);
        if (isActive) {
          setEnhancedResumePreviewUrl(null);
        }
      }
    };

    loadPreview();

    return () => {
      isActive = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [enhancementResult?.pdfUrl]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, jobsRes] = await Promise.all([
          api.get('/users/me/profile'),
          api.get('/placements/jobs'),
        ]);
        setProfile(profileRes.data);
        setJobs(jobsRes.data);

        // Fetch applications for this student
        if (profileRes.data.id) {
          try {
            const appsRes = await api.get(`/placements/student/${profileRes.data.id}/applications`);
            const appsMap: ApplicationStatus = {};
            appsRes.data.forEach((app: any) => {
              appsMap[app.job_id] = {
                applied: true,
                status: app.status,
                id: app.id
              };
            });
            setApplications(appsMap);
          } catch (err) {
            console.error('Error fetching applications:', err);
          }
        }
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

  const handleApply = (job: Job) => {
    if (!profile?.id) {
      alert('Student profile not found');
      return;
    }
    setSelectedJobForApplication(job);
    setApplicationForm({ resume: null, coverLetter: '' });
    setShowApplicationModal(true);
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setApplicationForm((prev) => ({
        ...prev,
        resume: e.target.files![0]
      }));
    }
  };

  const handleCoverLetterChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setApplicationForm((prev) => ({
      ...prev,
      coverLetter: e.target.value
    }));
  };

  const handleSubmitApplication = async () => {
    if (!selectedJobForApplication || !profile?.id) {
      alert('Invalid application data');
      return;
    }

    setSubmittingApplication(true);

    try {
      let resumeData = '';
      let resumeFilename = '';

      // Convert file to base64 if provided
      if (applicationForm.resume) {
        resumeFilename = applicationForm.resume.name;
        const reader = new FileReader();
        resumeData = await new Promise((resolve, reject) => {
          reader.onload = () => {
            const base64 = reader.result as string;
            resolve(base64.split(',')[1]); // Get base64 without data:application/...
          };
          reader.onerror = reject;
          reader.readAsDataURL(applicationForm.resume!);
        }) as string;
      }

      const response = await api.post('/placements/apply', {
        student_id: profile.id,
        job_id: selectedJobForApplication.id,
        resume_data: resumeData,
        resume_filename: resumeFilename,
        cover_letter: applicationForm.coverLetter
      });

      // Update applications state
      setApplications((prev) => ({
        ...prev,
        [selectedJobForApplication.id]: {
          applied: true,
          status: response.data.status,
          id: response.data.id
        }
      }));

      // Close modal and show success
      setShowApplicationModal(false);
      alert('Application submitted successfully!');
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || 'Failed to submit application';
      alert(errorMessage);
    } finally {
      setSubmittingApplication(false);
    }
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

  const handleEnhancerResumeChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0];
    if (!nextFile) return;

    setResumeFile(nextFile);
    setResumeJson(null);
    setAtsResult(null);
    setSuggestions([]);
    setEnhancementResult(null);
    setEnhancedResumePreviewUrl(null);
    setResumeEnhancerError(null);
    setResumeUploadMessage('Uploading resume...');

    try {
      const formData = new FormData();
      formData.append('resume', nextFile);

      const response = await axios.post(`${NODE_API_BASE_URL}/api/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResumeUploadMessage(
        response.data?.message || 'Resume uploaded successfully and ready for ATS analysis.'
      );
    } catch (err: any) {
      console.error('Resume upload failed', err);
      setResumeUploadMessage('');
      setResumeEnhancerError(
        err?.response?.data?.message || 'Resume upload failed. Please check the Node service on port 5000.'
      );
    }
  };

  const handleRunAtsAnalysis = async () => {
    if (!resumeFile) {
      setResumeEnhancerError('Upload a resume before running ATS analysis.');
      return;
    }

    if (!jobDescription.trim()) {
      setResumeEnhancerError('Paste the target job description before running ATS analysis.');
      return;
    }

    setAnalyzingResume(true);
    setResumeEnhancerError(null);
    setEnhancementResult(null);

    try {
      const parseFormData = new FormData();
      parseFormData.append('file', resumeFile);

      const parseResponse = await axios.post(`${AI_API_BASE_URL}/parse-resume`, parseFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const parsedResume = parseResponse.data?.data || parseResponse.data;
      setResumeJson(parsedResume);

      const payload = {
        resume_json: parsedResume,
        job_description: jobDescription,
      };

      const [scoreResponse, analysisResponse] = await Promise.all([
        axios.post(`${AI_API_BASE_URL}/score-from-json`, payload),
        axios.post(`${AI_API_BASE_URL}/analyze-from-json`, payload),
      ]);

      const nextAtsResult = parseScore(scoreResponse.data?.data || scoreResponse.data);
      setAtsResult(nextAtsResult);
      setSuggestions(extractSuggestions(analysisResponse.data?.data || analysisResponse.data));
    } catch (err: any) {
      console.error('ATS analysis failed', err);
      setResumeEnhancerError(
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        'ATS analysis failed. Please verify the AI service on port 8001.'
      );
    } finally {
      setAnalyzingResume(false);
    }
  };

  const handleEnhanceResume = async () => {
    if (!resumeJson) {
      setResumeEnhancerError('Run ATS analysis first so the resume can be parsed and enhanced.');
      return;
    }

    if (!jobDescription.trim()) {
      setResumeEnhancerError('A job description is required to enhance the resume.');
      return;
    }

    setEnhancingResume(true);
    setResumeEnhancerError(null);

    try {
      const response = await axios.post(`${AI_API_BASE_URL}/enhance-resume`, {
        resume_json: resumeJson,
        job_description: jobDescription,
      });

      const data = response.data?.data || response.data;
      setEnhancementResult({
        originalScore: data?.original_score ?? atsResult?.score ?? null,
        enhancedScore: data?.enhanced_score ?? null,
        pdfUrl: buildPdfUrl(data?.pdf_url || null),
      });
    } catch (err: any) {
      console.error('Enhance resume failed', err);
      setResumeEnhancerError(
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        'Resume enhancement failed. Please retry once the AI service is healthy.'
      );
    } finally {
      setEnhancingResume(false);
    }
  };

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

  const atsRingDegrees = Math.max(0, Math.min((atsResult?.score ?? 0) * 3.6, 360));

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
          <button
            className={`sd-nav-item ${activeSection === 'opportunities' ? 'sd-nav-active' : ''}`}
            type="button"
            onClick={() => setActiveSection('opportunities')}
          >
            <Briefcase size={18} /> Opportunities
          </button>
          <button
            className={`sd-nav-item ${activeSection === 'profile' ? 'sd-nav-active' : ''}`}
            type="button"
            onClick={() => setActiveSection('profile')}
          >
            <User size={18} /> My Profile
          </button>
          <button
            className={`sd-nav-item ${activeSection === 'resume-enhancer' ? 'sd-nav-active' : ''}`}
            type="button"
            onClick={() => setActiveSection('resume-enhancer')}
          >
            <Sparkles size={18} /> Resume Enhancer
          </button>
        </nav>

        <button className="sd-logout-btn" onClick={handleLogout}>
          <LogOut size={16} /> Logout
        </button>
      </aside>

      {/* MAIN CONTENT */}
      <main className="sd-main">

        {activeSection !== 'resume-enhancer' && (
        <>
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
        </>
        )}

        {activeSection === 'profile' && (
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
        )}

        {activeSection === 'resume-enhancer' && (
        <section className="sd-card" id="resume-enhancer-section">
          <div className="sd-enhancer-hero">
            <div className="sd-enhancer-hero-copy">
              <span className="sd-enhancer-eyebrow">Student AI Tools</span>
              <div className="sd-card-header sd-enhancer-header">
                <Sparkles size={20} />
                <h2>Resume Enhancer</h2>
              </div>
              <p className="sd-enhancer-subtitle">
                Upload your resume, compare it against a role, review ATS feedback, and generate a stronger version ready to download.
              </p>
            </div>
            <div className="sd-enhancer-summary">
              <div className="sd-enhancer-summary-item">
                <span>Resume</span>
                <strong>{resumeFile ? 'Uploaded' : 'Pending'}</strong>
              </div>
              <div className="sd-enhancer-summary-item">
                <span>ATS</span>
                <strong>{atsResult?.score ?? '--'}</strong>
              </div>
              <div className="sd-enhancer-summary-item">
                <span>Enhanced</span>
                <strong>{enhancementResult?.enhancedScore ?? '--'}</strong>
              </div>
            </div>
          </div>

          <div className="sd-resume-layout">
            <div className="sd-resume-form-panel sd-workspace-panel">
              <div className="sd-panel-heading">
                <h3>Input</h3>
                <p>Provide the resume and target role details.</p>
              </div>

              <div className="sd-form-group sd-form-surface">
                <label className="sd-form-label">Upload Resume</label>
                <div
                  className="sd-file-input-wrapper sd-resume-upload"
                  onClick={() => resumeEnhancerInputRef.current?.click()}
                >
                  <Upload size={28} color="#4f46e5" />
                  <p className="sd-file-input-text">
                    {resumeFile ? resumeFile.name : 'Choose PDF, DOC, or DOCX resume'}
                  </p>
                  <p className="sd-file-input-hint">
                    Stored on the Node service, then analyzed by the AI service.
                  </p>
                  <input
                    ref={resumeEnhancerInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleEnhancerResumeChange}
                    className="sd-file-input-hidden"
                  />
                </div>
                {resumeUploadMessage && <p className="sd-upload-success">{resumeUploadMessage}</p>}
              </div>

              <div className="sd-form-group sd-form-surface">
                <label className="sd-form-label">Job Description</label>
                <textarea
                  className="sd-textarea sd-jd-textarea"
                  placeholder="Paste the full job description here to score and improve the resume for that role."
                  value={jobDescription}
                  onChange={(event) => setJobDescription(event.target.value)}
                  rows={10}
                />
                <p className="sd-hint-text">{jobDescription.trim().length} characters</p>
              </div>

              {resumeEnhancerError && (
                <div className="sd-resume-error">
                  <AlertCircle size={16} />
                  <span>{resumeEnhancerError}</span>
                </div>
              )}

              <div className="sd-resume-actions">
                <button
                  className="sd-btn-primary-modal"
                  onClick={handleRunAtsAnalysis}
                  disabled={analyzingResume || !resumeFile || !jobDescription.trim()}
                >
                  {analyzingResume ? (
                    <>
                      <Loader2 size={16} className="sd-spinner-inline" />
                      Calculating ATS Score...
                    </>
                  ) : (
                    <>
                      <BarChart3 size={16} />
                      See ATS Score
                    </>
                  )}
                </button>

                <button
                  className="sd-btn-secondary"
                  onClick={handleEnhanceResume}
                  disabled={enhancingResume || !resumeJson}
                >
                  {enhancingResume ? (
                    <>
                      <Loader2 size={16} className="sd-spinner-inline" />
                      Enhancing Resume...
                    </>
                  ) : (
                    <>
                      <WandSparkles size={16} />
                      Enhance Resume
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="sd-resume-output-panel">
              {!atsResult && !enhancementResult && (
                <div className="sd-preview-card sd-workspace-panel">
                  <div className="sd-preview-header">
                    <div>
                      <h3>Uploaded Resume</h3>
                      <p>Review the uploaded file before running ATS analysis.</p>
                    </div>
                    {resumeFile && (
                      <span className="sd-preview-file-tag">
                        <FileText size={14} />
                        {resumeFile.name}
                      </span>
                    )}
                  </div>

                  {resumePreviewUrl ? (
                    resumeFile?.type === 'application/pdf' ? (
                      <iframe
                        className="sd-resume-preview-frame"
                        src={resumePreviewUrl}
                        title="Uploaded resume preview"
                      />
                    ) : (
                      <div className="sd-file-preview-fallback">
                        <FileText size={36} />
                        <p>{resumeFile?.name}</p>
                        <span>Preview is available for PDF resumes. DOC and DOCX files will still be analyzed.</span>
                      </div>
                    )
                  ) : (
                    <div className="sd-file-preview-fallback">
                      <Upload size={36} />
                      <p>No resume uploaded yet</p>
                      <span>Select a resume to start the ATS and enhancement workflow.</span>
                    </div>
                  )}
                </div>
              )}

              {atsResult && !enhancementResult && (
                <div className="sd-analysis-stage sd-workspace-panel">
                  <div className="sd-analysis-card-header">
                    <div className="sd-inline-heading">
                      <BarChart3 size={18} />
                      <h3>ATS Analysis</h3>
                    </div>
                    <span className="sd-preview-file-tag">Step 2</span>
                  </div>

                  <div className="sd-analysis-stage-grid">
                    <div className="sd-analysis-stage-score">
                      <div
                        className="sd-score-ring"
                        style={{
                          background: `radial-gradient(circle at center, #fff 48%, transparent 49%), conic-gradient(#4f46e5 0deg, #4f46e5 ${atsRingDegrees}deg, #e2e8f0 ${atsRingDegrees}deg, #e2e8f0 360deg)`,
                        }}
                      >
                        <strong>{atsResult.score ?? '--'}</strong>
                        <span>/100</span>
                      </div>
                      <p className="sd-score-summary">{atsResult.summary}</p>
                    </div>

                    <div className="sd-analysis-stage-feedback">
                      <div className="sd-keywords-grid">
                        <div>
                          <p className="sd-keyword-heading">Matched Keywords</p>
                          <div className="sd-chip-wrap">
                            {atsResult.matchedKeywords.length > 0 ? atsResult.matchedKeywords.map((item) => (
                              <span key={item} className="sd-keyword-chip sd-keyword-chip-good">{item}</span>
                            )) : <span className="sd-muted-text">No matched keywords returned.</span>}
                          </div>
                        </div>
                        <div>
                          <p className="sd-keyword-heading">Missing Keywords</p>
                          <div className="sd-chip-wrap">
                            {atsResult.missingKeywords.length > 0 ? atsResult.missingKeywords.map((item) => (
                              <span key={item} className="sd-keyword-chip sd-keyword-chip-warn">{item}</span>
                            )) : <span className="sd-muted-text">No missing keywords returned.</span>}
                          </div>
                        </div>
                      </div>

                      <div className="sd-suggestion-panel">
                        <p className="sd-keyword-heading">Suggestions</p>
                        {suggestions.length > 0 ? (
                          <ul className="sd-suggestion-list">
                            {suggestions.map((suggestion) => (
                              <li key={suggestion}>{suggestion}</li>
                            ))}
                          </ul>
                        ) : (
                          <p className="sd-muted-text">Targeted suggestions will appear here after analysis.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {enhancementResult && (
                <div className="sd-enhanced-card sd-workspace-panel">
                  <div className="sd-analysis-card-header">
                    <div className="sd-inline-heading">
                      <WandSparkles size={18} />
                      <h3>Enhanced Resume</h3>
                    </div>
                    {enhancementResult.pdfUrl && (
                      <a
                        className="sd-download-link"
                        href={enhancementResult.pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                      >
                        <Download size={16} />
                        Download PDF
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                  <div className="sd-enhanced-score-row">
                    <div className="sd-enhanced-score-box">
                      <span>Original</span>
                      <strong>{enhancementResult.originalScore ?? '--'}</strong>
                    </div>
                    <div className="sd-enhanced-score-box sd-enhanced-score-box-good">
                      <span>Enhanced</span>
                      <strong>{enhancementResult.enhancedScore ?? '--'}</strong>
                    </div>
                  </div>

                  {enhancedResumePreviewUrl ? (
                    <iframe
                      className="sd-resume-preview-frame"
                      src={enhancedResumePreviewUrl}
                      title="Enhanced resume preview"
                    />
                  ) : (
                    <div className="sd-file-preview-fallback">
                      <FileText size={36} />
                      <p>Enhanced resume generated</p>
                      <span>The preview is unavailable, but you can still use the download button if a PDF is returned.</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
        )}

        {/* JOB OPPORTUNITIES */}
        {activeSection === 'opportunities' && (
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

                    {/* Apply Button Section */}
                    <div className="sd-job-action">
                      {applications[job.id]?.applied ? (
                        <div className="sd-applied-badge">
                          <CheckCircle size={16} className="sd-applied-icon" />
                          <span>Applied - {applications[job.id]?.status}</span>
                        </div>
                      ) : eligible ? (
                        <button
                          className="sd-apply-btn"
                          onClick={() => handleApply(job)}
                        >
                          <Send size={16} />
                          Apply Now
                        </button>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
        )}

        {/* APPLICATION MODAL */}
        {showApplicationModal && selectedJobForApplication && (
          <div className="sd-modal-overlay" onClick={() => setShowApplicationModal(false)}>
            <div className="sd-modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="sd-modal-header">
                <div>
                  <h2 className="sd-modal-title">Apply for {selectedJobForApplication.job_role}</h2>
                  <p className="sd-modal-subtitle">at {selectedJobForApplication.company_name}</p>
                </div>
                <button
                  className="sd-modal-close"
                  onClick={() => setShowApplicationModal(false)}
                  type="button"
                >
                  <X size={24} />
                </button>
              </div>

              <div className="sd-modal-body">
                {/* Resume Upload */}
                <div className="sd-form-group">
                  <label className="sd-form-label">📄 Upload Resume <span style={{ color: '#ef4444' }}>*</span></label>
                  <div
                    className="sd-file-input-wrapper"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload size={32} color="#4f46e5" />
                    <p className="sd-file-input-text">
                      {applicationForm.resume
                        ? applicationForm.resume.name
                        : 'Click to upload or drag and drop'}
                    </p>
                    <p className="sd-file-input-hint">PDF, DOC, DOCX (max 5MB)</p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleResumeChange}
                      className="sd-file-input-hidden"
                    />
                  </div>
                </div>

                {/* Cover Letter */}
                <div className="sd-form-group">
                  <label className="sd-form-label">✍️ Cover Letter</label>
                  <textarea
                    className="sd-textarea"
                    placeholder="Tell us why you're a great fit for this role... (Optional)"
                    value={applicationForm.coverLetter}
                    onChange={handleCoverLetterChange}
                    rows={6}
                  />
                  <p className="sd-hint-text">{applicationForm.coverLetter.length} characters</p>
                </div>
              </div>

              <div className="sd-modal-footer">
                <button
                  className="sd-btn-secondary"
                  onClick={() => setShowApplicationModal(false)}
                  disabled={submittingApplication}
                >
                  Cancel
                </button>
                <button
                  className="sd-btn-primary-modal"
                  onClick={handleSubmitApplication}
                  disabled={submittingApplication || !applicationForm.resume}
                >
                  {submittingApplication ? (
                    <>
                      <Loader2 size={16} className="sd-spinner-inline" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Submit Application
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default StudentDashboard;
