import { io, type Socket } from 'socket.io-client';
import { PUBLIC_API } from '$env/static/public';

let socket: Socket | null = $state(null);
let connected = $state(false);

export function connectSocket() {
	if (socket) return;
	socket = io(PUBLIC_API, { withCredentials: true });
	socket.on('connect', () => { connected = true; });
	socket.on('disconnect', () => { connected = false; });
}

export function disconnectSocket() {
	socket?.disconnect();
	socket = null;
	connected = false;
}

export function getSocket() {
	return socket;
}

export function isConnected() {
	return connected;
}
