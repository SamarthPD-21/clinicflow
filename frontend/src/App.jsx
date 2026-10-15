import { useCallback, useEffect, useState } from 'react';
import { api, todayISO } from './api.js';
import Appointments from './components/Appointments.jsx';
import BookingForm from './components/BookingForm.jsx';
import Dashboard from './components/Dashboard.jsx';
import Doctors from './components/Doctors.jsx';
import Modal from './components/Modal.jsx';
import Patients from './components/Patients.jsx';

const VIEWS = [
  ['dashboard', 'Dashboard', '▦'],
  ['appointments', 'Appointments', '◷'],
  ['doctors', 'Doctors', '✚'],
  ['patients', 'Patients', '☺'],
];

export default function App() {
  const [view, setView] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [today, setToday] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [version, setVersion] = useState(0);
  const [booking, setBooking] = useState(false);
  const [toast, setToast] = useState(null);
  const [offline, setOffline] = useState(false);

  const notify = useCallback((message, error = false) => {
    setToast({ message, error });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const refresh = useCallback(() => setVersion((v) => v + 1), []);

  useEffect(() => {
    Promise.all([api.stats(), api.appointments({ day: todayISO() }), api.doctors(), api.patients()])
      .then(([s, t, d, p]) => {
        setStats(s);
        setToday(t);
        setDoctors(d);
        setPatients(p);
        setOffline(false);
      })
      .catch(() => setOffline(true));
  }, [version]);

  async function changeStatus(appt, status) {
    try {
      await api.updateAppointment(appt.id, { status });
      notify(`${appt.patient_name}: ${status.replace('_', ' ').toLowerCase()}`);
      refresh();
    } catch (err) {
      notify(err.message, true);
    }
  }

  async function remove(appt) {
    if (!window.confirm(`Delete ${appt.patient_name}'s appointment?`)) return;
    await api.deleteAppointment(appt.id);
    notify('Appointment deleted');
    refresh();
  }

  const title = VIEWS.find(([k]) => k === view)[1];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="logo" aria-hidden="true">✚</span>
          <div><strong>ClinicFlow</strong><small>Front desk</small></div>
        </div>
        <nav>
          {VIEWS.map(([key, label, icon]) => (
            <button key={key} className={view === key ? 'active' : ''} onClick={() => setView(key)} aria-current={view === key ? 'page' : undefined}>
              <span aria-hidden="true">{icon}</span>{label}
            </button>
          ))}
        </nav>
        <div className={`env ${offline ? 'down' : 'up'}`}>
          <span className="dot" />{offline ? 'API unreachable' : 'API connected'}
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <h1>{title}</h1>
            <p className="muted">Sunrise Family Clinic</p>
          </div>
          <button className="btn primary" onClick={() => setBooking(true)}>+ Book appointment</button>
        </header>

        {offline && (
          <div className="banner" role="alert">
            Cannot reach the ClinicFlow API. Check that the backend is running and <code>/api</code> is routed to it.
          </div>
        )}

        {view === 'dashboard' && <Dashboard stats={stats} today={today} onStatus={changeStatus} />}
        {view === 'appointments' && <Appointments doctors={doctors} version={version} onStatus={changeStatus} onDelete={remove} />}
        {view === 'doctors' && <Doctors doctors={doctors} onChange={refresh} notify={notify} />}
        {view === 'patients' && <Patients version={version} onChange={refresh} notify={notify} />}
      </main>

      {booking && (
        <Modal title="Book appointment" onClose={() => setBooking(false)}>
          <BookingForm
            doctors={doctors.filter((d) => d.active)}
            patients={patients}
            onDone={() => {
              setBooking(false);
              notify('Appointment booked');
              refresh();
            }}
          />
        </Modal>
      )}

      {toast && <div className={`toast ${toast.error ? 'error' : ''}`} role="status">{toast.message}</div>}
    </div>
  );
}
