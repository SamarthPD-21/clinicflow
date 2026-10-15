// All calls are relative: Nginx (Compose) or the Ingress (Kubernetes) routes /api to the backend.
async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join(', ')
      : data.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return data;
}

const qs = (params) => {
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v != null));
  const s = new URLSearchParams(clean).toString();
  return s ? `?${s}` : '';
};

export const api = {
  stats: () => request('/api/appointments/stats'),
  appointments: (params = {}) => request(`/api/appointments${qs(params)}`),
  createAppointment: (body) => request('/api/appointments', { method: 'POST', body }),
  updateAppointment: (id, body) => request(`/api/appointments/${id}`, { method: 'PUT', body }),
  deleteAppointment: (id) => request(`/api/appointments/${id}`, { method: 'DELETE' }),
  doctors: (params = {}) => request(`/api/doctors${qs(params)}`),
  createDoctor: (body) => request('/api/doctors', { method: 'POST', body }),
  updateDoctor: (id, body) => request(`/api/doctors/${id}`, { method: 'PUT', body }),
  deleteDoctor: (id) => request(`/api/doctors/${id}`, { method: 'DELETE' }),
  patients: (params = {}) => request(`/api/patients${qs(params)}`),
  createPatient: (body) => request('/api/patients', { method: 'POST', body }),
  deletePatient: (id) => request(`/api/patients/${id}`, { method: 'DELETE' }),
};

export const STATUSES = ['SCHEDULED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED', 'NO_SHOW'];

export const statusLabel = (s) => s.replace('_', ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase());

export const todayISO = () => {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
};

export const fmtTime = (iso) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
export const fmtDate = (iso) =>
  new Date(iso).toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
