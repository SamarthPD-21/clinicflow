import { statusLabel } from '../api.js';

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status.toLowerCase()}`}>{statusLabel(status)}</span>;
}
