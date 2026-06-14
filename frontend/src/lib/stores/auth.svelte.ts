import { goto } from '$app/navigation';
import { getMe, login as apiLogin, logout as apiLogout } from '$lib/services/api';

let currentUser = $state<{ user_id: number; role: string; email: string; username: string } | null>(null);

export const auth = {
	get user() {
		return currentUser;
	},
	get isAuthenticated() {
		return currentUser !== null;
	},
	get role() {
		return currentUser?.role ?? null;
	},

	async login(credential: string, password: string) {
		const res = await apiLogin(credential, password);
		currentUser = res.user;
		return res;
	},

	async logout() {
		await apiLogout();
		currentUser = null;
		await goto('/auth/login');
	},

	async checkAuth() {
		try {
			const res = await getMe();
			currentUser = {
				user_id: res.message.user_id,
				role: res.message.role,
				email: res.message.email,
				username: res.message.username
			};
			return true;
		} catch {
			currentUser = null;
			return false;
		}
	},

	clear() {
		currentUser = null;
	},

	redirectAfterLogin() {
		const role = currentUser?.role;
		if (role === 'admin') {
			window.location.href = '/admin';
		} else if (role === 'agent') {
			window.location.href = '/agent';
		} else if (role === 'customer') {
			window.location.href = '/portal';
		} else if (role === 'finance_staff') {
			window.location.href = '/finance_staff';
		} else if (role === 'service_advisor') {
			window.location.href = '/service_advisor';
		} else if (role === 'service_staff') {
			window.location.href = '/service_staff';
		}
	}
};
