import React, { useState, useEffect } from 'react';
import { Download, Eye, MessageCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import api from '../services/api';
import './AdminApplications.css';

interface Application {
  id: number;
  student_id: number;
  student_name: string;
  student_email: string;
  student_cgpa: number;
  student_branch: string;
  job_id: number;
  job_role: string;
  company_name: string;
  status: string;
  applied_at: string;
  resume_filename?: string;
  has_resume: boolean;
  cover_letter?: string;
}

interface ApplicationDetails {
  id: number;
  student: {
    id: number;
    name: string;
    reg_number: string;
    email: string;
    cgpa: number;
    branch: string;
    graduation_year: number;
    active_backlogs: number;
  };
  job: {
    id: number;
    company_name: string;
    job_role: string;
    description: string;
    location: string;
    min_cgpa: number;
  };
  status: string;
  applied_at: string;
  resume_filename?: string;
  has_resume: boolean;
  cover_letter?: string;
}

const AdminApplications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApplication, setSelectedApplication] = useState<ApplicationDetails | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showCoverLetterModal, setShowCoverLetterModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/placements/applications/all');
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
      alert('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const fetchApplicationDetails = async (applicationId: number) => {
    try {
      const response = await api.get(`/placements/applications/${applicationId}`);
      setSelectedApplication(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error fetching application details:', error);
      alert('Failed to load application details');
    }
  };

  const downloadResume = async (applicationId: number, filename?: string) => {
    try {
      setDownloadingId(applicationId);
      const response = await api.get(`/placements/applications/${applicationId}/resume`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || `resume_${applicationId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      alert('Failed to download resume');
    } finally {
      setDownloadingId(null);
    }
  };

  const updateApplicationStatus = async (applicationId: number, newStatus: string) => {
    try {
      await api.put(`/placements/applications/${applicationId}/status`, {
        status: newStatus
      });
      
      // Refresh the application details
      if (selectedApplication && selectedApplication.id === applicationId) {
        await fetchApplicationDetails(applicationId);
      }
      
      // Refresh the applications list
      await fetchApplications();
      alert('Application status updated successfully');
    } catch (error) {
      console.error('Error updating application status:', error);
      alert('Failed to update application status');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
      case 'interview scheduled':
        return <CheckCircle className="status-icon" style={{ color: '#10b981' }} />;
      case 'rejected':
        return <XCircle className="status-icon" style={{ color: '#ef4444' }} />;
      case 'pending':
        return <Clock className="status-icon" style={{ color: '#f59e0b' }} />;
      default:
        return <Clock className="status-icon" style={{ color: '#6b7280' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
      case 'interview scheduled':
        return 'status-badge status-approved';
      case 'rejected':
        return 'status-badge status-rejected';
      case 'pending':
        return 'status-badge status-pending';
      default:
        return 'status-badge';
    }
  };

  const filteredApplications = filterStatus === 'all'
    ? applications
    : applications.filter(app => app.status.toLowerCase() === filterStatus.toLowerCase());

  if (loading) {
    return (
      <div className="admin-applications-container">
        <div className="loading-spinner">Loading applications...</div>
      </div>
    );
  }

  return (
    <div className="admin-applications-container">
      <div className="admin-header">
        <h1>Student Applications</h1>
        <p className="header-subtitle">Review and manage student job applications</p>
      </div>

      <div className="admin-toolbar">
        <div className="filter-section">
          <label>Filter by Status:</label>
          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
            className="status-filter"
          >
            <option value="all">All Applications</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="interview scheduled">Interview Scheduled</option>
          </select>
        </div>
        <div className="app-count">
          {filteredApplications.length} application{filteredApplications.length !== 1 ? 's' : ''}
        </div>
      </div>

      {filteredApplications.length === 0 ? (
        <div className="empty-state">
          <p>No applications found</p>
        </div>
      ) : (
        <div className="applications-list">
          <table className="applications-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Registration</th>
                <th>Job Role</th>
                <th>Company</th>
                <th>CGPA</th>
                <th>Applied Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredApplications.map((application) => (
                <tr key={application.id} className="application-row">
                  <td>
                    <div className="student-name">{application.student_name}</div>
                  </td>
                  <td>{application.student_email}</td>
                  <td>{application.job_role}</td>
                  <td>{application.company_name}</td>
                  <td>
                    <span className={application.student_cgpa >= 3.0 ? 'cgpa-good' : 'cgpa-warning'}>
                      {application.student_cgpa.toFixed(2)}
                    </span>
                  </td>
                  <td>{new Date(application.applied_at).toLocaleDateString()}</td>
                  <td>
                    <div className={getStatusColor(application.status)}>
                      {getStatusIcon(application.status)}
                      {application.status}
                    </div>
                  </td>
                  <td>
                    <div className="actions-cell">
                      {application.has_resume && (
                        <>
                          <button
                            className="action-btn download-btn"
                            onClick={() => downloadResume(application.id, application.resume_filename)}
                            disabled={downloadingId === application.id}
                            title="Download Resume"
                          >
                            <Download size={16} />
                            {downloadingId === application.id ? 'Downloading...' : 'Resume'}
                          </button>
                        </>
                      )}
                      {application.cover_letter && (
                        <button
                          className="action-btn view-btn"
                          onClick={() => {
                            setSelectedApplication({
                              ...application,
                              student: {
                                id: application.student_id,
                                name: application.student_name,
                                reg_number: application.student_email,
                                email: application.student_email,
                                cgpa: application.student_cgpa,
                                branch: application.student_branch,
                                graduation_year: 0,
                                active_backlogs: 0
                              },
                              job: {
                                id: application.job_id,
                                company_name: application.company_name,
                                job_role: application.job_role,
                                description: '',
                                location: '',
                                min_cgpa: 0
                              }
                            });
                            setShowCoverLetterModal(true);
                          }}
                          title="View Cover Letter"
                        >
                          <MessageCircle size={16} />
                          Cover Letter
                        </button>
                      )}
                      <button
                        className="action-btn details-btn"
                        onClick={() => fetchApplicationDetails(application.id)}
                        title="View Full Details"
                      >
                        <Eye size={16} />
                        Details
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedApplication && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Application Details</h2>
              <button
                className="close-btn"
                onClick={() => setShowDetailModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h3>Student Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Name:</label>
                    <p>{selectedApplication.student.name}</p>
                  </div>
                  <div className="detail-item">
                    <label>Registration:</label>
                    <p>{selectedApplication.student.reg_number}</p>
                  </div>
                  <div className="detail-item">
                    <label>CGPA:</label>
                    <p>{selectedApplication.student.cgpa.toFixed(2)}</p>
                  </div>
                  <div className="detail-item">
                    <label>Branch:</label>
                    <p>{selectedApplication.student.branch}</p>
                  </div>
                  <div className="detail-item">
                    <label>Active Backlogs:</label>
                    <p>{selectedApplication.student.active_backlogs}</p>
                  </div>
                  <div className="detail-item">
                    <label>Graduation Year:</label>
                    <p>{selectedApplication.student.graduation_year}</p>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Job Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Company:</label>
                    <p>{selectedApplication.job.company_name}</p>
                  </div>
                  <div className="detail-item">
                    <label>Position:</label>
                    <p>{selectedApplication.job.job_role}</p>
                  </div>
                  <div className="detail-item">
                    <label>Location:</label>
                    <p>{selectedApplication.job.location}</p>
                  </div>
                  <div className="detail-item">
                    <label>Minimum CGPA:</label>
                    <p>{selectedApplication.job.min_cgpa.toFixed(2)}</p>
                  </div>
                </div>
                <div className="detail-item full-width">
                  <label>Job Description:</label>
                  <p>{selectedApplication.job.description}</p>
                </div>
              </div>

              <div className="detail-section">
                <h3>Application Details</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Applied Date:</label>
                    <p>{new Date(selectedApplication.applied_at).toLocaleString()}</p>
                  </div>
                  <div className="detail-item">
                    <label>Status:</label>
                    <p>
                      <span className={getStatusColor(selectedApplication.status)}>
                        {selectedApplication.status}
                      </span>
                    </p>
                  </div>
                  {selectedApplication.resume_filename && (
                    <div className="detail-item">
                      <label>Resume File:</label>
                      <p>{selectedApplication.resume_filename}</p>
                    </div>
                  )}
                </div>
                {selectedApplication.cover_letter && (
                  <div className="detail-item full-width">
                    <label>Cover Letter:</label>
                    <p className="cover-letter-preview">{selectedApplication.cover_letter}</p>
                  </div>
                )}
              </div>

              <div className="detail-section">
                <h3>Update Status</h3>
                <div className="status-buttons">
                  <button
                    className="status-action-btn status-approve"
                    onClick={() => updateApplicationStatus(selectedApplication.id, 'approved')}
                  >
                    Approve
                  </button>
                  <button
                    className="status-action-btn status-reject"
                    onClick={() => updateApplicationStatus(selectedApplication.id, 'rejected')}
                  >
                    Reject
                  </button>
                  <button
                    className="status-action-btn status-interview"
                    onClick={() => updateApplicationStatus(selectedApplication.id, 'interview scheduled')}
                  >
                    Schedule Interview
                  </button>
                </div>
              </div>

              {selectedApplication.has_resume && (
                <div className="modal-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => downloadResume(selectedApplication.id, selectedApplication.resume_filename)}
                    disabled={downloadingId === selectedApplication.id}
                  >
                    <Download size={18} />
                    {downloadingId === selectedApplication.id ? 'Downloading...' : 'Download Resume'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Cover Letter Modal */}
      {showCoverLetterModal && selectedApplication && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Cover Letter - {selectedApplication.student.name}</h2>
              <button
                className="close-btn"
                onClick={() => setShowCoverLetterModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="cover-letter-container">
                <div className="cover-letter-meta">
                  <p><strong>Position:</strong> {selectedApplication.job.job_role} at {selectedApplication.job.company_name}</p>
                  <p><strong>Applied:</strong> {new Date(selectedApplication.applied_at).toLocaleDateString()}</p>
                </div>
                <div className="cover-letter-text">
                  {selectedApplication.cover_letter}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminApplications;
