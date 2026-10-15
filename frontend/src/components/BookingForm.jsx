import { useState } from 'react';
import { api, todayISO } from '../api.js';

export default function BookingForm({ doctors, patients, onDone }) {
  const [form, setForm] = useState({
    doctor_id: doctors[0]?.id ?? '',
    patient_id: patients[0]?.id ?? '',
    date: todayISO(),
    time: '10:00',
    reason: '',
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await api.createAppointment({
        doctor_id: Number(form.doctor_id),
        patient_id: Number(form.patient_id),
        scheduled_at: `${form.date}T${form.time}:00`,
        reason: form.reason,
      });
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (!doctors.length || !patients.length) {
    return <p className="muted pad">Add at least one active doctor and one patient before booking.</p>;
  }

  return (
    <form className="form" onSubmit={submit}>
      <label>
        Doctor
        <select value={form.doctor_id} onChange={set('doctor_id')}>
          {doctors.map((d) => (
            <option key={d.id} value={d.id}>{d.name} — {d.specialty}</option>
          ))}
        </select>
      </label>
      <label>
        Patient
        <select value={form.patient_id} onChange={set('patient_id')}>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>{p.full_name} · {p.phone}</option>
          ))}
        </select>
      </label>
      <div className="row">
        <label>
          Date
          <input type="date" value={form.date} onChange={set('date')} required />
        </label>
        <label>
          Time
          <input type="time" step="900" value={form.time} onChange={set('time')} required />
        </label>
      </div>
      <label>
        Reason for visit
        <textarea rows="3" value={form.reason} onChange={set('reason')} placeholder="e.g. Follow-up, fever, annual check-up" />
      </label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button type="submit" className="btn primary" disabled={saving}>{saving ? 'Booking…' : 'Book appointment'}</button>
      </div>
    </form>
  );
}
