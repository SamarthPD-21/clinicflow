import { useEffect, useState } from 'react';
import { api } from '../api.js';

const EMPTY = { full_name: '', phone: '', email: '', date_of_birth: '' };

export default function Patients({ version, onChange, notify }) {
  const [q, setQ] = useState('');
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  useEffect(() => {
    const t = setTimeout(() => api.patients({ q }).then(setRows, (e) => notify(e.message, true)), 200);
    return () => clearTimeout(t);
  }, [q, version, notify]);

  async function add(e) {
    e.preventDefault();
    try {
      await api.createPatient(form);
      setForm(EMPTY);
      notify('Patient registered');
      onChange();
    } catch (err) {
      notify(err.message, true);
    }
  }

  return (
    <div className="grid-2 wide-left">
      <section className="card">
        <header className="card-head wrap">
          <h2>Patients</h2>
          <input className="search" type="search" placeholder="Search name or phone" value={q} onChange={(e) => setQ(e.target.value)} />
        </header>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Name</th><th>Phone</th><th>Email</th><th>Date of birth</th></tr></thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.id}>
                  <td data-label="Name"><strong>{p.full_name}</strong></td>
                  <td data-label="Phone">{p.phone}</td>
                  <td data-label="Email">{p.email || <span className="muted">—</span>}</td>
                  <td data-label="Date of birth">{p.date_of_birth || <span className="muted">—</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && <p className="empty">No patients found.</p>}
        </div>
      </section>
      <section className="card">
        <header className="card-head"><h2>Register patient</h2></header>
        <form className="form" onSubmit={add}>
          <label>Full name<input value={form.full_name} onChange={set('full_name')} required /></label>
          <label>Phone<input value={form.phone} onChange={set('phone')} placeholder="+91 98xxx xxxxx" required /></label>
          <label>Email<input type="email" value={form.email} onChange={set('email')} /></label>
          <label>Date of birth<input type="date" value={form.date_of_birth} onChange={set('date_of_birth')} /></label>
          <div className="form-actions"><button className="btn primary">Register</button></div>
        </form>
      </section>
    </div>
  );
}
