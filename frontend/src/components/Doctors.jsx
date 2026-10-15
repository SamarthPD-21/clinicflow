import { useState } from 'react';
import { api } from '../api.js';

export default function Doctors({ doctors, onChange, notify }) {
  const [form, setForm] = useState({ name: '', specialty: '', room: '' });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function add(e) {
    e.preventDefault();
    try {
      await api.createDoctor(form);
      setForm({ name: '', specialty: '', room: '' });
      notify('Doctor added');
      onChange();
    } catch (err) {
      notify(err.message, true);
    }
  }

  const toggle = async (d) => {
    await api.updateDoctor(d.id, { active: !d.active });
    onChange();
  };

  return (
    <div className="grid-2 wide-left">
      <section className="card">
        <header className="card-head"><h2>Doctors</h2><span className="muted">{doctors.length} on staff</span></header>
        <ul className="people">
          {doctors.map((d) => (
            <li key={d.id} className={d.active ? '' : 'inactive'}>
              <span className="avatar" aria-hidden="true">{d.name.replace('Dr. ', '').split(' ').map((p) => p[0]).join('').slice(0, 2)}</span>
              <div>
                <strong>{d.name}</strong>
                <span className="muted">{d.specialty}{d.room && ` · Room ${d.room}`}</span>
              </div>
              <button className="btn small" onClick={() => toggle(d)}>{d.active ? 'Mark away' : 'Mark available'}</button>
            </li>
          ))}
        </ul>
      </section>
      <section className="card">
        <header className="card-head"><h2>Add doctor</h2></header>
        <form className="form" onSubmit={add}>
          <label>Name<input value={form.name} onChange={set('name')} placeholder="Dr. Full Name" required /></label>
          <label>Specialty<input value={form.specialty} onChange={set('specialty')} placeholder="e.g. Orthopedics" required /></label>
          <label>Room<input value={form.room} onChange={set('room')} placeholder="e.g. 204" /></label>
          <div className="form-actions"><button className="btn primary">Add doctor</button></div>
        </form>
      </section>
    </div>
  );
}
