import { useEffect, useState } from 'react';
import { STATUSES, api, fmtDate, fmtTime, statusLabel } from '../api.js';
import StatusBadge from './StatusBadge.jsx';

const NEXT_ACTIONS = {
  SCHEDULED: [['CHECKED_IN', 'Check in'], ['CANCELLED', 'Cancel'], ['NO_SHOW', 'No-show']],
  CHECKED_IN: [['COMPLETED', 'Complete']],
};

export default function Appointments({ doctors, version, onStatus, onDelete }) {
  const [filters, setFilters] = useState({ day: '', status: '', doctor_id: '' });
  const [rows, setRows] = useState(null);
  const [error, setError] = useState('');
  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  useEffect(() => {
    api.appointments(filters).then(setRows, (e) => setError(e.message));
  }, [filters, version]);

  return (
    <section className="card">
      <header className="card-head wrap">
        <h2>Appointments</h2>
        <div className="filters">
          <input type="date" aria-label="Filter by day" value={filters.day} onChange={set('day')} />
          <select aria-label="Filter by status" value={filters.status} onChange={set('status')}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{statusLabel(s)}</option>)}
          </select>
          <select aria-label="Filter by doctor" value={filters.doctor_id} onChange={set('doctor_id')}>
            <option value="">All doctors</option>
            {doctors.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
      </header>
      {error && <p className="form-error">{error}</p>}
      {rows === null ? (
        <p className="empty">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="empty">No appointments match these filters.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>When</th><th>Patient</th><th>Doctor</th><th>Reason</th><th>Status</th><th aria-label="Actions" /></tr>
            </thead>
            <tbody>
              {rows.map((a) => (
                <tr key={a.id}>
                  <td data-label="When"><strong>{fmtTime(a.scheduled_at)}</strong> <span className="muted">{fmtDate(a.scheduled_at)}</span></td>
                  <td data-label="Patient">{a.patient_name}</td>
                  <td data-label="Doctor">{a.doctor_name}<br /><span className="muted">{a.doctor_specialty}</span></td>
                  <td data-label="Reason">{a.reason || <span className="muted">—</span>}</td>
                  <td data-label="Status"><StatusBadge status={a.status} /></td>
                  <td className="actions">
                    {(NEXT_ACTIONS[a.status] ?? []).map(([s, label]) => (
                      <button key={s} className="btn small" onClick={() => onStatus(a, s)}>{label}</button>
                    ))}
                    <button className="btn small danger" onClick={() => onDelete(a)} aria-label={`Delete appointment ${a.id}`}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
