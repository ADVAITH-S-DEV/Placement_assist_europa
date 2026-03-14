import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import api from '../services/api';
import { useRef } from 'react';

const AdminCalendar = () => {
  const calendarRef = useRef<FullCalendar | null>(null);

  const handleSelect = async (info: any) => {
    const params = new URLSearchParams(window.location.search);
    const studentId = Number(params.get('studentId'));
    const jobId = Number(params.get('jobId'));

    if (!studentId || !jobId) {
      alert('Missing student or job information in the URL.');
      return;
    }

    // Ask admin to confirm the chosen slot (date + time window)
    const startDisplay = new Date(info.startStr).toLocaleString();
    const endDisplay = new Date(info.endStr).toLocaleString();
    const confirmStart = window.confirm(
      `Schedule interview for this student?\n\nStart: ${startDisplay}\nEnd: ${endDisplay}`
    );
    if (!confirmStart) return;

    try {
      await api.post('/placements/schedule-interview', {
        student_id: studentId,
        job_id: jobId,
        start: info.startStr,
        end: info.endStr
      });
      alert('Interview scheduled and added to the calendar.');
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        'Failed to schedule interview. Please try a different time slot.';
      alert(message);
    }
  };

  const handleEventClick = async (clickInfo: any) => {
    const interviewId = clickInfo.event.id;
    const title = clickInfo.event.title;

    const confirmDelete = window.confirm(
      `Do you want to remove this interview?\n\n${title}\n\nYou can then schedule a new slot if needed.`
    );
    if (!confirmDelete) return;

    try {
      await api.delete(`/placements/interviews/${interviewId}`);
      // Refresh events on the calendar
      const apiInstance = (calendarRef.current as any)?.getApi?.();
      apiInstance?.refetchEvents();
      alert('Interview removed.');
    } catch (err) {
      alert('Failed to remove interview. Please try again.');
    }
  };

  return (
    <FullCalendar
      ref={calendarRef as any}
      plugins={[timeGridPlugin, interactionPlugin]}
      initialView="timeGridWeek"
      selectable={true}
      select={handleSelect}
      eventClick={handleEventClick}
      // Improve readability / visibility of time slots
      height="auto"
      slotLabelFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      eventTimeFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      eventDisplay="block"
      eventColor="#4f46e5"
      eventTextColor="#ffffff"
      eventDidMount={(info: any) => {
        const el = info.el as HTMLElement;
        el.style.fontSize = '0.8rem';
        el.style.padding = '2px 4px';
        el.style.borderRadius = '4px';
        el.style.whiteSpace = 'normal';
        el.style.lineHeight = '1.2';
      }}
      // Point FullCalendar directly to the FastAPI backend
      events="http://localhost:8000/placements/calendar-events"
    />
  );
};

export default AdminCalendar;