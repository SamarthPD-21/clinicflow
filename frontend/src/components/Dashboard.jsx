import { STATUSES, fmtTime, statusLabel } from '../api.js';
import StatusBadge from './StatusBadge.jsx';

function Kpi({ label, value, hint }) {
  return (
    <div className="kpi">
      <span className="kpi-label">{label}</span>
      <strong className="kpi-value">{value}</strong>
      {hint && <span className="kpi-hint">{hint}</span>}
    </div>
  );
}

export default function Dashboard({ stats, today, onStatus }) {
  const total = Object.values(stats?.by_status ?? {}).reduce((a, b) => a + b, 0);
  const now = new Date();
  const next = today.find((a) => a.status === 'SCHEDULED' && new Date(a.scheduled_at) >= now);

  return (
    <>
      <section className="kpis">
        <Kpi label="Today's appointments" value={stats?.appointments_today ?? '–'} hint={next ? `Next at ${fmtTime(next.scheduled_at)}` : 'No more today'} />
        <Kpi label="Upcoming bookings" value={stats?.upcoming ?? '–'} hint="Scheduled or checked in" />
        <Kpi label="Active doctors" value={stats?.doctors ?? '–'} />
        <Kpi label="Registered patients" value={stats?.patients ?? '–'} />
        <Kpi label="Completion rate" value={stats ? `${Math.round(stats.completion_rate * 100)}%` : '–'} hint="Completed vs. no-show" />
      </section>

      <div className="grid-2">
        <section className="card">
          <header className="card-head">
            <h2>Today's schedule</h2>
            <span className="muted">{now.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long' })}</span>
          </header>
          {today.length === 0 ? (
            <p className="empty">No appointments booked for today.</p>
          ) : (
            <ol className="timeline">
              {today.map((a) => (
                <li key={a.id} className={`slot slot-${a.status.toLowerCase()}`}>
                  <time>{fmtTime(a.scheduled_at)}</time>
                  <div className="slot-body">
                    <strong>{a.patient_name}</strong>
                    <span className="muted">{a.doctor_name} · {a.reason || a.doctor_specialty}</span>
                  </div>
                  <StatusBadge status={a.status} />
                  {a.status === 'SCHEDULED' && (
                    <button className="btn small" onClick={() => onStatus(a, 'CHECKED_IN')}>Check in</button>
                  )}
                  {a.status === 'CHECKED_IN' && (
                    <button className="btn small primary" onClick={() => onStatus(a, 'COMPLETED')}>Complete</button>
                  )}
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="card">
          <header className="card-head"><h2>Status breakdown</h2><span className="muted">{total} total</span></header>
          <ul className="bars">
            {STATUSES.map((s) => {
              const n = stats?.by_status?.[s] ?? 0;
              return (
                <li key={s}>
                  <span>{statusLabel(s)}</span>
                  <div className="bar"><div className={`bar-fill fill-${s.toLowerCase()}`} style={{ width: total ? `${(n / total) * 100}%` : 0 }} /></div>
                  <strong>{n}</strong>
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </>
  );
}
