function parseDT(dt: string | Date | null | undefined): Date | null {
	if (!dt) return null;
	if (typeof dt === 'object') return dt;
	const s = String(dt);
	if (!s.includes('Z') && !s.includes('+')) {
		return new Date(s + '+08:00');
	}
	return new Date(s);
}

export function formatSlotDateTime(dt: string | Date | null | undefined): string {
	const d = parseDT(dt);
	if (!d || isNaN(d.getTime())) return '—';
	return (
		d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) +
		' · ' +
		d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
	);
}

export function formatDateShort(dt: string | Date | null | undefined): string {
	const d = parseDT(dt);
	if (!d || isNaN(d.getTime())) return '—';
	return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function formatSlotOption(s: {
	slot_datetime?: string | Date | null;
	slot_type?: string | null;
	remaining?: number | null;
	capacity?: number | null;
}): string {
	const d = parseDT(s.slot_datetime);
	if (!d || isNaN(d.getTime())) return '—';
	const datePart = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
	const timePart = d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
	const type = s.slot_type ? ' — ' + s.slot_type.charAt(0).toUpperCase() + s.slot_type.slice(1).replace(/_/g, ' ') : '';
	const r = s.remaining ?? s.capacity ?? 0;
	return `${datePart} · ${timePart}${type} — ${r} slot${r !== 1 ? 's' : ''} left`;
}
