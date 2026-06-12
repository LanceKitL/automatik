import { PUBLIC_API } from '$env/static/public';

async function request<T>(
	method: string,
	path: string,
	body?: Record<string, unknown>
): Promise<T> {
	const res = await fetch(`${PUBLIC_API}${path}`, {
		method,
		headers: body ? { 'Content-Type': 'application/json' } : undefined,
		credentials: 'include',
		body: body ? JSON.stringify(body) : undefined
	});

	const data = await res.json();

	if (!res.ok) {
		throw new Error(data.message || `Request failed with status ${res.status}`);
	}

	return data as T;
}

export interface LoginResponse {
	message: string;
	user: {
		user_id: number;
		role: string;
		email: string;
		username: string;
	};
}

export interface MeResponse {
	message: {
		user_id: number;
		username: string;
		email: string;
		role: string;
	};
	current_ip: string;
}

export function login(credential: string, password: string) {
	return request<LoginResponse>('POST', '/auth/login', {
		username: credential,
		email: credential,
		password
	});
}

export function logout() {
	return request<{ message: string }>('POST', '/auth/logout');
}

export function getMe() {
	return request<MeResponse>('GET', '/auth/me');
}

export function changePassword(
	old_password: string,
	new_password: string,
	confirm_password: string
) {
	return request<{ message: string }>('PUT', '/auth/changePassword', {
		old_password,
		new_password,
		confirm_password
	});
}

export function forgotPassword(email: string) {
	return request<{ message: string }>('POST', '/auth/forgot-password', { email });
}

export interface ResetPasswordParams {
	token_id: string;
	raw_token: string;
	new_password: string;
	confirm_password: string;
}

export function resetPassword(params: ResetPasswordParams) {
	return request<{ message: string }>('POST', '/auth/reset-password', params);
}

export function getUsers() {
	return request<ListResponse>('GET', '/admin/users');
}

export function getUserById(id: number) {
	return request<SingleUserResponse>('GET', `/admin/users/${id}`);
}

export function createUser(data: CreateUserPayload) {
	return request<{ message: string; user_id: number; role: string }>('POST', '/admin/users', data);
}

export function updateUser(id: number, data: UpdateUserPayload) {
	return request<UpdateResponse>('PUT', `/admin/users/update/${id}`, data);
}

export function updateUserProfile(id: number, data: UpdateProfilePayload) {
	return request<UpdateResponse>('PUT', `/admin/users/${id}/profile`, data);
}

export function deleteUser(id: number) {
	return request<{ message: string }>('DELETE', `/admin/users/${id}/delete`);
}

export function getAgentDetail(id: number) {
	return request<SingleUserResponse>('GET', `/admin/agents/${id}`);
}

export function getCustomerSalesHistory(id: number) {
	return request<ListResponse>('GET', `/admin/customer/${id}/sales`);
}

export function getAdminVehicles() {
	return request<ListResponse>('GET', '/admin/vehicles');
}

export function getSuppliers() {
	return request<ListResponse>('GET', '/admin/suppliers/');
}

export function createSupplier(data: Record<string, unknown>) {
	return request<{ message: string; supplier_id: number }>('POST', '/admin/suppliers/', data);
}

export function updateSupplier(id: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/admin/suppliers/${id}`, data);
}

export function deleteSupplier(id: number) {
	return request<{ message: string }>('DELETE', `/admin/suppliers/${id}`);
}

export function getSupplies() {
	return request<ListResponse>('GET', '/admin/supplies/');
}

export function createSupply(data: Record<string, unknown>) {
	return request<{ message: string; supply_id: number }>('POST', '/admin/supplies/', data);
}

export function updateSupply(id: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/admin/supplies/${id}`, data);
}

export function deleteSupply(id: number) {
	return request<{ message: string }>('DELETE', `/admin/supplies/${id}`);
}

export function getAdminInventory() {
	return request<InventoryResponse>('GET', '/admin/inventory');
}

export function createVehicle(data: Record<string, unknown>) {
	return request<{ message: string }>('POST', '/vehicles/create', data);
}

export function updateVehicle(id: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/vehicles/update/${id}`, data);
}

export function deleteVehicle(id: number) {
	return request<{ message: string }>('DELETE', `/vehicles/delete/${id}`);
}

export function updateVehicleStatus(id: number, status: string) {
	return request<{ message: string }>('PUT', `/vehicles/update/status/${id}`, { status });
}

export async function uploadVehiclePhoto(vehicleId: number, file: File): Promise<{ message: string; photo_url: string }> {
	const formData = new FormData();
	formData.append('file', file);
	formData.append('vehicle_id', String(vehicleId));

	const res = await fetch(`${PUBLIC_API}/admin/inventory/photos`, {
		method: 'POST',
		credentials: 'include',
		body: formData
	});

	const data = await res.json();
	if (!res.ok) {
		throw new Error(data.message || 'Photo upload failed');
	}
	return data;
}

export function getInquiries() {
	return request<InquiryListResponse>('GET', '/inquiries/');
}

export function assignInquiry(inquiryId: number, agentId: number) {
	return request<{ message: string }>('PUT', `/inquiries/assign/${inquiryId}`, { agent_id: agentId });
}

export function closeInquiry(inquiryId: number) {
	return request<{ message: string }>('PUT', `/inquiries/close/${inquiryId}`);
}

export function selfAssignInquiry(inquiryId: number) {
	return request<{ message: string }>('PUT', `/inquiries/self-assign/${inquiryId}`);
}

export function convertInquiryToSale(inquiryId: number, data: {
	selling_price: number;
	payment_type: string;
	loan_amount?: number;
	interest_rate?: number;
	term_months?: number;
	down_payment?: number;
}) {
	return request<{ message: string; sale_id: number }>('PUT', `/inquiries/convert-to-sale/${inquiryId}`, data);
}

export function resolveInquiry(inquiryId: number) {
	return request<{ message: string }>('PUT', `/inquiries/resolve/${inquiryId}`);
}

export function sendInquiryEmail(inquiryId: number, data: { subject: string; body: string }) {
	return request<{ message: string }>('POST', `/inquiries/${inquiryId}/send-email`, data);
}

export function getAgentInquiries() {
	return request<{ data: InquiryItem[] }>('GET', '/agent/inquiries');
}

export function getAgentsList() {
	return request<ListResponse>('GET', '/admin/agents');
}

export function getSales() {
	return request<{ data: SaleListResponse }>('GET', '/admin/sales');
}

export function getSale(id: number) {
	return request<SingleUserResponse>('GET', `/admin/sales/${id}`);
}

export function createSale(data: Record<string, unknown>) {
	return request<{ message: string; sale_id: number; customer_id: number }>('POST', '/admin/sales', data);
}

export function updateSaleStatus(id: number, status: string) {
	return request<{ message: string }>('PUT', `/admin/sales/${id}/status`, { status });
}

export function getAvailableVehicles() {
	return request<ListResponse>('GET', '/vehicles');
}

export function getCustomersList() {
	return request<ListResponse>('GET', '/admin/customer');
}

export function updateContract(saleId: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/admin/sales/${saleId}/contract`, data);
}

export function addInsurance(saleId: number, data: Record<string, unknown>) {
	return request<{ insurance_id: number }>('POST', `/admin/sales/${saleId}/insurance`, data);
}

export function updateInsurance(insuranceId: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/admin/insurance/${insuranceId}`, data);
}

export function getLoans() {
	return request<ListResponse>('GET', '/admin/loans');
}

export function getPayments() {
	return request<ListResponse>('GET', '/admin/payments');
}

export function recordPayment(saleId: number, data: Record<string, unknown>) {
	return request<{ payment_id: number }>('POST', `/admin/sales/${saleId}/payments`, data);
}

export function getCommissions() {
	return request<unknown[]>('GET', '/admin/commissions');
}

export function getServiceBookings() {
	return request<ListResponse>('GET', '/admin/service/bookings');
}

export function getAdminWarrantyClaims() {
	return request<ListResponse>('GET', '/admin/service/warranty');
}

export function getAdminDocuments() {
	return request<unknown[]>('GET', '/admin/service/documents');
}

export function getAdminNotifications() {
	return request<ListResponse>('GET', '/admin/notifications');
}

export function getAuditLogs() {
	return request<ListResponse>('GET', '/admin/audit_logs');
}

export function getSettings() {
	return request<SettingsResponse>('GET', '/admin/settings');
}

export interface ListResponse {
	data: unknown[];
}

export interface SingleUserResponse {
	data: Record<string, unknown>;
}

export interface UpdateResponse {
	message: string;
	updated_fields: string[];
}

export interface CreateUserPayload {
	username: string;
	email: string;
	password: string;
	role: string;
	full_name?: string;
	phone_number?: string;
	address?: string;
	city?: string;
	province?: string;
	zip_code?: string;
	date_of_birth?: string;
	gender?: string;
}

export interface UpdateUserPayload {
	username?: string;
	email?: string;
	role?: string;
	is_active?: boolean;
}

export interface UpdateProfilePayload {
	full_name?: string;
	phone_number?: string;
	address?: string;
	city?: string;
	province?: string;
	zip_code?: string;
	date_of_birth?: string;
	gender?: string;
}

export interface SettingsResponse {
	data: Record<
		string,
		{
			setting_id: number;
			setting_key: string;
			setting_value: string;
			description: string | null;
			updated_by: number | null;
			updated_at: string | null;
		}
	>;
}

export function getAdminDashboard() {
	return request<AdminDashboardResponse>('GET', '/admin/dashboard');
}

export function getAgentDashboard() {
	return request<AgentDashboardResponse>('GET', '/agent/dashboard');
}

export function getCustomerDashboard() {
	return request<CustomerDashboardResponse>('GET', '/portal/');
}

export interface AdminDashboardResponse {
	data: {
		stats: {
			total_users: number;
			total_agents: number;
			total_customers: number;
			open_inquiries: number;
		};
		total_revenue: number;
		active_sales: number;
		recent_sales: unknown[];
		recent_bookings: unknown[];
		recent_warranty_claims: unknown[];
	};
}

export interface InventoryResponse {
	data: {
		vehicles: Record<string, unknown>[];
		suppliers: Record<string, unknown>[];
		supplies: Record<string, unknown>[];
		low_stock_threshold: number;
	};
}

export interface AgentDashboardResponse {
	data: {
		inquiries: unknown[];
		pending_tasks: unknown[];
		commissions_and_sales: { sale_id: number; selling_price: number; total_commission: number }[];
		commission_trend: { month: string; total_commission: number; total_revenue: number }[];
	};
}

// ── Finance Staff Portal ──────────────────────────────────────────────────

export function getFinanceDashboard() {
	return request<FinanceDashboardResponse>('GET', '/finance_staff/dashboard');
}

export function getFinanceLoans() {
	return request<{ data: LoanItem[] }>('GET', '/finance_staff/loans');
}

export function getFinanceLoansWithoutInsurance() {
	return request<{ data: LoanItem[] }>('GET', '/finance_staff/loans?without_insurance=true');
}

export function getFinanceLoan(id: number) {
	return request<{ data: LoanItem & { amortization_schedule: ScheduleItem[] } }>('GET', `/finance_staff/loans/${id}`);
}

export function updateFinanceLoanStatus(id: number, status: string) {
	return request<{ message: string }>('PUT', `/finance_staff/loans/${id}/status`, { bank_approval_status: status });
}

export function getEligibleSalesForLoan() {
	return request<{ data: EligibleSaleItem[] }>('GET', '/finance_staff/loans/eligible-sales');
}

export function createFinanceLoan(data: {
	sale_id: number;
	loan_amount: number;
	interest_rate: number;
	term_months: number;
	down_payment?: number;
}) {
	return request<{ loan_id: number }>('POST', '/finance_staff/loans', data);
}

export function getFinanceLoanSchedule(id: number) {
	return request<{ data: ScheduleItem[] }>('GET', `/finance_staff/loans/${id}/schedule`);
}

export function getFinancePayments() {
	return request<ListResponse>('GET', '/finance_staff/payments');
}

export function createFinancePayment(saleId: number, data: Record<string, unknown>) {
	return request<{ payment_id: number }>('POST', `/finance_staff/sales/${saleId}/payments`, data);
}

export function getFinanceInsurance() {
	return request<ListResponse>('GET', '/finance_staff/insurance');
}

export function getFinanceInsuranceDetail(id: number) {
	return request<{ data: Record<string, unknown> }>('GET', `/finance_staff/insurance/${id}`);
}

export function createFinanceInsurance(saleId: number, data: Record<string, unknown>) {
	return request<{ insurance_id: number }>('POST', `/finance_staff/sales/${saleId}/insurance`, data);
}

export function updateFinanceInsurance(id: number, data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/finance_staff/insurance/${id}`, data);
}

export function getMyPayments() {
	return request<ListResponse>('GET', '/portal/payments');
}

export async function uploadPaymentProof(paymentId: number, file: File): Promise<{ message: string; proof_of_payment: string }> {
	const formData = new FormData();
	formData.append('file', file);

	const res = await fetch(`${PUBLIC_API}/portal/payments/${paymentId}/upload-proof`, {
		method: 'POST',
		credentials: 'include',
		body: formData
	});

	const data = await res.json();
	if (!res.ok) {
		throw new Error(data.message || 'Upload failed');
	}
	return data;
}

export function getOverdueAmortizations() {
	return request<{ data: OverdueItem[] }>('GET', '/finance_staff/amortization/overdue');
}

export function updateAmortizationStatus(id: number, status: string) {
	return request<{ message: string }>('PUT', `/finance_staff/amortization/${id}/status`, { status });
}

// ── Service Advisor Portal ────────────────────────────────────────────────

export function getServiceAdvisorDashboard() {
	return request<ServiceAdvisorDashboardResponse>('GET', '/service_advisor/dashboard');
}

export function getAdvisorServiceBookings() {
	return request<ListResponse>('GET', '/service_advisor/bookings');
}

export function assignAndOpenIntake(bookingId: number) {
	return request<{ message: string; booking_id: number }>('PUT', `/service_advisor/bookings/${bookingId}/assign-intake`);
}

export function createEstimate(bookingId: number, estimateData: Record<string, unknown>) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${bookingId}/estimate`, { estimate_data: estimateData });
}

export function transmitEstimate(bookingId: number) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${bookingId}/transmit`);
}

export function signEstimate(bookingId: number) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${bookingId}/sign`);
}

export function getMyServiceBookings() {
	return request<ListResponse>('GET', '/service_advisor/bookings/mine');
}

export function selfAssignBooking(id: number) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${id}/assign`);
}

export function updateServiceBookingStatus(id: number, status: string) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${id}/status`, { status });
}

export function updateTechnicianNotes(id: number, notes: string) {
	return request<{ message: string }>('PUT', `/service_advisor/bookings/${id}/notes`, { technician_notes: notes });
}

export function getServiceAdvisorWarranty() {
	return request<ListResponse>('GET', '/service_advisor/warranty');
}

export function getServiceAdvisorWarrantyDetail(id: number) {
	return request<SingleUserResponse>('GET', `/service_advisor/warranty/${id}`);
}

// ── Response types ────────────────────────────────────────────────────────

export interface FinanceDashboardResponse {
	data: {
		pending_reviews: number;
		approved_contracting: number;
		total_financed_portfolio: number;
		delinquency_rate: number;
		total_collected: number;
		recent_payments: unknown[];
	};
}

export interface InquiryItem {
	inquiry_id: number;
	message: string;
	status: 'open' | 'assigned' | 'resolved' | 'closed';
	agent_assigned: number | null;
	agent_name: string | null;
	user_type: 'guest' | 'customer';
	created_at: string;
	contacts: {
		name: string | null;
		email: string | null;
		number: string | null;
	};
	vehicle: {
		id: number;
		brand: string;
		model: string;
		price: string;
	};
}

export type InquiryListResponse = InquiryItem[];

export interface ServiceAdvisorDashboardResponse {
	data: {
		pending_bookings: number;
		unassigned_bookings: number;
		my_assigned: number;
		today_bookings: number;
	};
}

export interface CustomerDashboardVehicle {
	vehicle_id?: number;
	brand?: string;
	model?: string;
	year?: string;
	color?: string;
	mileage?: string;
	fuel_type?: string;
	license_plate?: string;
	vin?: string;
}

export interface DocumentItem {
	document_id?: number;
	id?: number;
	document_name?: string;
	name?: string;
	type?: string;
	created_at?: string;
}

export interface DashboardNotification {
	id: number;
	title: string;
	message: string;
	is_read: boolean;
	created_at: string;
}

export interface CustomerDashboardResponse {
	data: {
		dashboard: {
			active_sales: number;
			next_payment_due: string | null;
			next_payment_amount: number | null;
			open_inquiries: number;
			unread_notification: number;
			recent_documents: DocumentItem[];
			my_vehicles: CustomerDashboardVehicle[];
		};
		notifications: DashboardNotification[];
		inquiries: unknown[];
		sales: unknown[];
	};
}

export interface SaleItem {
	sales: {
		sale_id: number;
		payment_type: string;
		sale_date: string;
		status: string;
		inquiry_id: number | null;
		selling_price: string;
	};
	customer: {
		username: string;
		email: string;
	};
	agent: {
		username: string;
		email: string;
	};
	vehicle: {
		vehicle_id: number;
		brand: string;
		model: string;
		body_type: string;
		price: string;
	};
}

export type SaleListResponse = SaleItem[];

// ── Loan & Amortization types ──────────────────────────────────────

export interface LoanItem {
	loan_id: number;
	sale_id: number;
	customer_name: string;
	brand: string;
	model: string;
	loan_amount: string;
	down_payment: string;
	interest_rate: string;
	term_months: number;
	monthly_amortization: string;
	bank_name: string;
	bank_approval_status: 'pending' | 'approved' | 'rejected';
}

export interface ScheduleItem {
	schedule_id: number;
	loan_id: number;
	month_number: number;
	due_date: string;
	principal: string;
	interest: string;
	total_due: string;
	running_balance: string;
	status: 'unpaid' | 'paid' | 'overdue';
	proof_of_payment?: string;
	payment_id?: number;
}

export interface OverdueItem {
	schedule_id: number;
	loan_id: number;
	sale_id: number;
	customer_name: string;
	customer_id: number;
	month_number: number;
	due_date: string;
	total_due: string;
	status: string;
}

export interface EligibleSaleItem {
	sale_id: number;
	selling_price: string;
	sale_date: string;
	customer_name: string;
	customer_id: number;
	brand: string;
	model: string;
	year: number;
	vehicle_id: number;
}

export interface NotificationItem {
	id: number;
	title: string;
	message: string;
	channel: string;
	ref_type: string;
	ref_id: number | null;
	is_read: boolean;
	created_at: string;
}

// Universal notification endpoints (work for all logged-in roles)
export function getRecentNotifications() {
	return request<{ data: NotificationItem[] }>('GET', '/notifications/recent');
}

export function getAllNotifications() {
	return request<{ data: NotificationItem[] }>('GET', '/notifications/all');
}

export function markNotificationRead(id: number) {
	return request<{ message: string }>('PUT', `/notifications/read/${id}`);
}

/** Resolve a vehicle photo URL — prepend backend origin for relative static paths. */
export function resolvePhotoUrl(url: string | null): string | null {
	if (!url) return null;
	if (url.startsWith('/')) return `${PUBLIC_API}${url}`;
	return url;
}

// --- Customer Portal: Vehicles, Inquiries, Test Drive ---

export interface VehiclePhoto {
	photo_id: number;
	vehicle_id: number;
	photo_url: string;
	sort_order: number;
	uploaded_at: string;
}

export interface VehicleSupplier {
	company_name: string;
	contact_name: string | null;
	contact_email: string | null;
	contact_phone: string | null;
	address: string | null;
}

export interface VehicleItem {
	vehicle_id: number;
	supplier_id: number;
	vin: string;
	brand: string;
	model: string;
	year: number;
	color: string | null;
	body_type: string | null;
	seating_capacity: number | null;
	transmission: string | null;
	fuel_type: string | null;
	price: string;
	status: string;
	specs_json: string | null;
	created_at: string;
	photos: VehiclePhoto[];
	supplier: VehicleSupplier | null;
}

export interface ServiceSlot {
	slot_id: number;
	slot_datetime: string;
	slot_type: string;
	capacity: number;
	is_available: number;
	remaining: number;
}

export function getCustomerPortalVehicles() {
	return request<{ data: VehicleItem[] }>('GET', '/portal/vehicles');
}

export function getVehicleDetail(id: number) {
	return request<{ data: VehicleItem }>('GET', `/portal/vehicles/${id}`);
}

export function submitInquiry(vehicle_id: number, message: string) {
	return request<{ message: string }>('POST', '/portal/inquiries', { vehicle_id, message });
}

export function getTestDriveSlots(date?: string, slot_type?: string) {
	const params = new URLSearchParams();
	if (slot_type) params.set('slot_type', slot_type);
	else params.set('slot_type', 'test_drive');
	if (date) params.set('date', date);
	return request<{ data: ServiceSlot[] }>('GET', `/service/slots?${params}`);
}

export function createBooking(slot_id: number, vehicle_id: number, booking_type: string) {
	return request<{ message: string; booking_id: number }>('POST', '/service/bookings', { slot_id, vehicle_id, booking_type });
}

export function reserveVehicle(vehicle_id: number) {
	return request<{ message: string }>('POST', `/portal/vehicles/${vehicle_id}/reserve`);
}

export function getPortalProfile() {
	return request<{ user: Record<string, unknown>; profile: Record<string, unknown>; customer_details?: Record<string, unknown> }>('GET', '/portal/profile');
}

export function updatePortalProfile(data: Record<string, unknown>) {
	return request<{ message: string }>('PUT', '/portal/profile', data);
}

export function getMyAmortization() {
	return request<{ data: Record<string, unknown>[] }>('GET', '/portal/amortization');
}

export function getAllDocuments() {
	return request<Record<string, unknown>[]>('GET', '/portal/documents');
}


