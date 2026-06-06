

AutoMatik — UI Requirements  |  Page 1CONFIDENTIAL — For Internal Use Only
AutoMatik
## Integrated Car Dealership & Management System
UI / UX Requirements Document
## Version 1.0 · Academic Year 2025–2026
Prepared for:Polytechnic University of the Philippines — CCIS
System:AutoMatik Web-Based Car Dealership & Management System
Document Type:UI / UX Requirements — Frontend Scope
Portals:Landing Page · Admin Portal · Agent Portal · Customer Portal
Tech Stack:React + Vite + Tailwind CSS (API: Flask / Python)
Date:June 2026

## Implementation Status Legend
The following annotations indicate the current backend implementation state for each feature:
- ✅ = **Implemented** — backend API endpoint exists and is fully functional
- ⚠️ = **Partial** — basic endpoint exists but lacks some documented functionality (e.g., filtering, pagination)
- ❌ = **Planned** — database table exists but no backend API endpoint has been built yet

AutoMatik — UI Requirements  |  Page 2CONFIDENTIAL — For Internal Use Only
Table of Contents
1Purpose & Scope
2General UI Conventions
3Landing Page
4Admin Portal
4.1Dashboard
4.2User Management
4.3Vehicle & Inventory Management
4.4Inquiries
4.5Sales & Contracts
4.6Loans & Amortization
4.7Payments
4.8Service Bookings & Slots
4.9Warranty Claims
4.10Documents
4.11Suppliers & Supplies
4.12Notifications
4.13Audit Logs
4.14System Settings
5Agent Portal
5.1Dashboard
5.2Inquiries
5.3Tasks
5.4Commissions
6Customer Portal
6.1Dashboard
6.2Vehicle Browse
6.3Sales & Contracts
6.4Loans & Amortization
6.5Payments

AutoMatik — UI Requirements  |  Page 3CONFIDENTIAL — For Internal Use Only
6.6Documents
6.7Service Bookings
6.8Warranty Claims
6.9Inquiries
6.10Notifications
6.11Profile Settings
7Global Components
8Data Field Reference

AutoMatik — UI Requirements  |  Page 4CONFIDENTIAL — For Internal Use Only
## 1. Purpose & Scope
This  document  defines  the  complete  User  Interface  (UI)  and  User  Experience  (UX)  requirements  for
AutoMatik  —  a  web-based  car  dealership  and  management  system.  It  covers  all  four  user-facing
portals: Landing Page, Admin Portal, Agent Portal, and Customer Portal.
Each section specifies sidebar navigation menus, page-level content, data fields displayed or captured,
and supporting UI components derived directly from the Flask API flow and MySQL database schema.
## 1.1 Document Scope
PortalPrimary UsersAccess Method
LandingPublic / GuestOpen URL — no login required
AdminAdministrator/ManagerUsername + password → session cookie
AgentSales AgentUsername + password → session cookie
CustomerRegistered CustomerUsername + password → session cookie
Note: ⚠️ The current backend implementation uses direct username/password login (same as Admin/Agent), not a token-based portal link. Customer accounts are created by Admin or Agent (via `POST /auth/customer/create`). Self-registration is not permitted.

AutoMatik — UI Requirements  |  Page 5CONFIDENTIAL — For Internal Use Only
- General UI Conventions
## 2.1 Layout
-   Two-column layout: fixed left sidebar (240 px) + main content area.
-   Top navigation bar: system logo, portal name, notification bell, user avatar with dropdown.
-   Responsive breakpoints: Desktop (≥1280 px), Tablet (768–1279 px), Mobile (<768 px).
-   Sidebar collapses to icon-only mode on tablet; bottom sheet on mobile.
## 2.2 Typography & Colors
-   Primary font: Calibri (web fallback: Helvetica Neue, sans-serif).
-   Base body size: 14 px / Line-height: 1.5.
-   Portal accent colors to differentiate role context (Admin: dark navy, Agent: steel blue, Customer:
teal).
-   Danger/Error: #E74C3C · Success: #27AE60 · Warning: #F39C12 · Info: #3498DB.
## 2.3 Forms & Validation
-   All required fields marked with an asterisk (*).
-   Inline validation — error message appears below field on blur.
-   Disabled submit button until all required fields pass validation.
-   Date pickers use ISO 8601 format (YYYY-MM-DD) internally; display as MM/DD/YYYY.
-   Currency fields formatted with comma separators and two decimal places (e.g., n 1,234,567.00).
## 2.4 Tables & Lists
-   All data tables include: search bar, column sort, pagination (10/25/50 rows per page), and export
## (CSV/PDF).
-   Status badges: color-coded chips (e.g., pending = gray, active = green, overdue = red).
-   Row actions: Edit, View, Delete — shown as icon buttons in last column.
-   Empty state: illustrated empty-state card with a call-to-action button.
## 2.5 Notifications & Feedback
-   Toast notifications (top-right, auto-dismiss 4 s) for CRUD success/failure.
-   Modal confirmations for irreversible actions (delete, cancel, mark paid).
-   Loading skeletons for data-heavy pages (tables, dashboard cards).
-   Notification bell icon shows unread count badge; dropdown shows last 5 alerts.

AutoMatik — UI Requirements  |  Page 6CONFIDENTIAL — For Internal Use Only
## 3. Landing Page
## LANDING PORTAL
Public-facing  marketing  site.  No  authentication  required.  Entry  point  for  guest  inquiries,  vehicle
browsing, chatbot, service slot viewing, and the payment calculator tool.
3.1 Navigation Bar (Top)
Nav ItemDestination / Behavior
LogoScrolls to Hero section
HomeHero / banner section
VehiclesVehicle listings section / page
AboutDealership info section
Contact / InquiryInquiry Form section
ServicesService booking info + slot calendar
LoginModal or redirect: /auth/login
## 3.2 Page Sections & Content
SectionContent DescriptionData Source / API
## Hero Banner
Full-width banner, headline, CTA buttons: 'Browse
Vehicles', 'Get a Quote'
Static / CMS
## Featured Vehicles
Grid of 4–6 vehicles: photo, brand, model, year, price,
'View Details' button
GET /vehicles (status=available)
## Vehicle Detail
Full specs, photo carousel, inquiry button, payment
calculator widget
GET /vehicles/
## Inquiry Form
Name*, email*, phone, vehicle selection dropdown,
message textarea
POST /inquiries
## Payment Calculator
Vehicle price, down payment, term (months), interest
rate → monthly estimate
Client-side formula (no API call)
## Service Slots  ❌ Planned
Calendar/list of available test drive slots; click to pre-fill
booking form
GET /service/slots
## Chatbot Widget  ❌ Planned
Floating button (bottom-right); opens chat drawer with
AI responses
POST /chatbot/message
About / ContactDealership address, hours, map embed, social linksStatic
FooterNav links, privacy policy, terms, copyrightStatic

AutoMatik — UI Requirements  |  Page 7CONFIDENTIAL — For Internal Use Only
## 3.3 Inquiry Form — Data Fields
FieldTypeRequiredDB Column
Full NameTextYesinquiries.guest_name
Email AddressEmailYesinquiries.guest_email
Phone NumberTelNoinquiries.guest_number
Vehicle InterestDropdownYesinquiries.vehicle_id
MessageTextareaYesinquiries.message

AutoMatik — UI Requirements  |  Page 8CONFIDENTIAL — For Internal Use Only
## 4. Admin Portal
## ADMIN PORTAL
Full  system  access.  Manages  all  entities:  users,  vehicles,  sales,  loans,  payments,  documents,
warranty, bookings, suppliers, audit logs, and settings.
## 4.0 Sidebar Navigation
Menu ItemIcon (suggestion)Sub-itemsStatus
## Dashboardgrid——✅
UsersusersAll Users · Agents · Customers✅
VehiclescarVehicle List · Add Vehicle · Low Stock✅
SupplierstruckSupplier List · Supplies / Parts✅ (Supplier) / ❌ (Supplies)
Inquiriesmessage-circleAll Inquiries · Chatbot Logs✅ (Inquiries) / ❌ (Chatbot Logs)
Salesshopping-cartAll Sales · Contracts · Insurance✅
Loanscredit-cardLoan List · Amortization · Overdue✅
Paymentsdollar-signPayment List · Summary✅
Commissionstrending-upCommission List · Agent Performance❌
Service BookingscalendarBookings · Slots Management❌
Warranty ClaimsshieldClaim List❌
Documentsfile-textDocument List❌
NotificationsbellSend Notification⚠️ (List: ✅ / Broadcast: ❌)
## Audit Logsactivity—
SettingssettingsSystem Settings
## 4.1 Dashboard
KPI CardValue SourceDrill-down Target
## Total Vehicles AvailableCOUNT vehicles WHERE status=availableVehicle List
## Total Sales (Month)
COUNT sales WHERE
MONTH(sale_date)=current
## Sales List
Revenue (Month)SUM selling_price WHERE month=currentSales Summary
Pending InquiriesCOUNT inquiries WHERE status=openInquiry List

AutoMatik — UI Requirements  |  Page 9CONFIDENTIAL — For Internal Use Only
KPI CardValue SourceDrill-down Target
Overdue AmortizationsCOUNT amortization WHERE status=overdueAmortization Overdue
Unpaid Commissions  ❌ PlannedCOUNT commissions WHERE is_paid=0Commission List
Pending Warranty Claims  ❌ PlannedCOUNT warranty WHERE status=submittedWarranty List
-   Recent Activity Feed  ⚠️ Partial: last 10 audit_logs with actor name, action, table, timestamp. (Backend `/logs` endpoint returns all records without LIMIT or filters.)
-   Sales Chart  ⚠️ Partial: Bar chart — monthly revenue for last 6 months. (Aggregation queries not yet exposed as a dedicated API.)
-   Top Agents Widget  ❌ Planned: ranked by commission_amount DESC for current month. (No dedicated endpoint.)
## 4.2 User Management
-   User List Table: user_id, full_name, email, role badge, is_active toggle, last_login, actions.
-   Create/Edit User Modal: username, email, password, role selector, profile fields.
-   Agent Detail: employee_number, hire_date, default_commission_rate, total sales count.
-   Customer Detail: customer_number, preferred_contact, preferred_payment, sales history list.
## 4.3 Vehicle & Inventory Management  ✅ (Vehicles) / ❌ Planned (Supplies/Parts)
FieldTypeDB Column
BrandTextvehicles.brand
ModelTextvehicles.model
YearNumbervehicles.year
ColorTextvehicles.color
Body TypeTextvehicles.body_type
TransmissionSelectvehicles.transmission
Fuel TypeSelectvehicles.fuel_type
Price (n)Decimalvehicles.price
StatusSelectvehicles.status
Specs (JSON)Textareavehicles.specs_json
PhotosFile Uploadvehicle_photos.photo_url
SupplierDropdownvehicles.supplier_id → suppliers.company_name
-   Status transition controls: available → reserved → delivered, any → discontinued.
-   Low-stock alert badge: shown when available count < threshold (from system_settings).
## 4.4 Inquiries
-   List table: inquiry_id, guest_name / user full_name, vehicle, status badge, created_at, assigned
agent.
-   Detail drawer: message thread, vehicle info card, assign agent dropdown, status action buttons.

AutoMatik — UI Requirements  |  Page 10CONFIDENTIAL — For Internal Use Only
-   Chatbot Logs sub-page  ❌ Planned: session_id, user_message, bot_response, intent_tag, timestamp.
## 4.5 Sales & Contracts
FieldTypeDB Column
VehicleDropdownsales.vehicle_id (status=available)
CustomerDropdownsales.customer_id
AgentDropdownsales.agent_id
Selling PriceDecimalsales.selling_price
Payment TypeSelectsales.payment_type (cash / installment)
Sale DateDatesales.sale_date
Inquiry LinkDropdownsales.inquiry_id (optional)
Contract URLFile/URLsales_contracts.contract_url
Contract StatusSelectsales_contracts.status
Insurance ProviderTextinsurance_records.provider_name
Policy NumberTextinsurance_records.policy_number
Coverage TypeTextinsurance_records.coverage_type
## 4.6 Loans & Amortization
FieldTypeDB Column
Down Payment (n)Decimalloan_details.down_payment
Loan Amount (n)Decimalloan_details.loan_amount
Interest Rate (%)Decimalloan_details.interest_rate
Term (months)Numberloan_details.term_months
Monthly Amort.Computedloan_details.monthly_amortization (auto-calc)
Bank NameTextloan_details.bank_name
Bank ApprovalSelectloan_details.bank_approval_status
-   Amortization Schedule Table: month #, due_date, principal, interest, total_due, running_balance,
status badge, mark-paid button.
-   Overdue sub-page: filtered view of status=overdue rows with customer and sale context.
## 4.7 Payments
FieldTypeDB Column
SaleDropdownpayments.sale_id

AutoMatik — UI Requirements  |  Page 11CONFIDENTIAL — For Internal Use Only
FieldTypeDB Column
Schedule RowDropdownpayments.schedule_id (if installment)
Amount Paid (n)Decimalpayments.amount_paid
Payment MethodSelectpayments.payment_method
Reference #Textpayments.reference
Recorded ByAutopayments.recorded_by (session user)
Payment DateDatepayments.payment_date
-   Payment Summary card: total collected, total pending, total overdue — grouped by month.
## 4.8 Service Bookings & Slots  ❌ Planned
-   Slots Management: create/edit slots with slot_datetime, slot_type (test_drive / maintenance /
repair), capacity, is_available toggle.
-   Bookings List: booking_id, customer name, vehicle, slot datetime, booking_type,
warranty_claim_id (if any), status badge, confirm/complete action buttons.
-   Calendar view (optional enhancement): visual grid of slots with booking count per slot.
## 4.9 Warranty Claims  ❌ Planned
-   List table: claim_id, customer name, vehicle, claim_type badge, status badge, submitted_at,
reviewed_by.
-   Detail page: description text, status action buttons (under_review → approved / rejected),
resolution textarea, linked service_bookings.
## 4.10 Documents  ❌ Planned
Document TypeEnum ValueDescription
Official ReceiptORCash payment proof
Certificate of Reg.CRLTO registration document
Warranty Certificatewarranty_certVehicle warranty PDF
Amortization PDFamortization_scheduleGenerated payment schedule
Sales Contractsales_contractSigned contract PDF
OtherotherMiscellaneous documents
-   Upload: file_url input, document_type select, sale linkage, is_accessible toggle.
## 4.11 Suppliers & Supplies  ✅ (Suppliers) / ❌ Planned (Supplies/Parts)
-   Supplier List: company_name, contact_name, contact_email, contact_phone, is_active toggle.
-   Supplier Detail: supplier info + linked vehicles count + supplies/parts list.

AutoMatik — UI Requirements  |  Page 12CONFIDENTIAL — For Internal Use Only
-   Supplies List  ❌ Planned: part_name, part_number, unit_cost, stock_qty, reorder_level, supplier name,
low-stock alert row highlight.
## 4.12 Notifications  ⚠️ Partial  (List/mark-read: ✅; Broadcast form: ❌ Planned)
-   Broadcast form  ❌ Planned: select target (user_id or role), title, message, channel (in_app / email / sms). (Utility function `brodcast_notif()` exists but no admin-facing API endpoint yet.)
-   Auto-trigger events displayed in a read-only log for admin reference.
## 4.13 Audit Logs  ⚠️ Partial
-   Table: log_id, user (actor), action badge (INSERT/UPDATE/DELETE), table_name, record_id,
ip_address, created_at. (Basic `GET /logs` returns all records unfiltered.)
-   Detail panel  ❌ Planned: old_value JSON vs new_value JSON diff viewer (side-by-side or unified diff).
-   Filters  ❌ Planned: action type, table_name, user_id, date range. Paginated (50 rows default).
## 4.14 System Settings  ❌ Planned
KeyDescriptionInput Type
default_commission_rateFallback agent commission rate (%)Decimal
chatbot_enabledToggle AI chatbot endpoint on/offBoolean Toggle
max_loan_term_monthsCap for loan term validationNumber
-   Each setting row: key (read-only), current value (editable), description, last updated by,
updated_at timestamp.

AutoMatik — UI Requirements  |  Page 13CONFIDENTIAL — For Internal Use Only
## 5. Agent Portal
## AGENT PORTAL
Sales agent workspace. Focused on managing assigned inquiries, tracking tasks, monitoring personal
commissions, and handling customer follow-ups.
## 5.0 Sidebar Navigation
Menu ItemSub-itemsStatus
## Dashboard——✅
InquiriesAssigned Inquiries✅
TasksMy Tasks · Create Task❌
CommissionsMy Earnings❌
ProfileView / Edit Profile✅
## 5.1 Agent Dashboard
WidgetData Source
Assigned Inquiries CountCOUNT inquiries WHERE agent_id=me AND status=assigned
Pending TasksCOUNT agent_tasks WHERE agent_id=me AND status=pending
Total Commissions (Month)SUM commission_amount WHERE agent_id=me AND month=current
Unpaid CommissionsSUM commission_amount WHERE agent_id=me AND is_paid=0
Recent SalesSELECT sales WHERE agent_id=me ORDER BY sale_date DESC LIMIT 5
## 5.2 Agent Inquiries  ✅
-   List table: inquiry_id, customer/guest name, vehicle, message preview, status badge, created_at.
-   Detail drawer: full message, vehicle info card, customer contact details, status action (resolve),
linked tasks.
-   Resolve button: sets status=resolved, resolved_at=NOW().
## 5.3 Agent Tasks  ❌ Planned
FieldTypeDB Column
Task TypeSelectagent_tasks.task_type (follow_up / appointment / demo / document_prep / other)
TitleTextagent_tasks.title

AutoMatik — UI Requirements  |  Page 14CONFIDENTIAL — For Internal Use Only
FieldTypeDB Column
Due DateDateTimeagent_tasks.due_date
StatusSelectagent_tasks.status
Linked InquiryDropdownagent_tasks.inquiry_id (optional)
NotesTextareaagent_tasks.notes
-   Kanban board view (optional): columns for pending / in_progress / done / cancelled.
## 5.4 Agent Commissions  ❌ Planned  (Agent self-service view; admin mark-paid endpoint also not yet built.)
-   List table: commission_id, sale vehicle (brand + model), selling_price, rate_applied (%),
commission_amount, is_paid badge, paid_at.
-   Summary card: total earned (all time), total paid, total pending.
Note: Agents view only; marking commissions paid is an Admin-only action.

AutoMatik — UI Requirements  |  Page 15CONFIDENTIAL — For Internal Use Only
## 6. Customer Portal
## CUSTOMER PORTAL
Post-purchase  self-service  portal.  Customers  access  their  sales,  loan  schedules,  documents,  service
bookings,  warranty  claims,  and  inquiries.  Access  is  granted  via  username/password  login  (not
token-based). Customer accounts are created by Admin or Agent.
## 6.0 Sidebar Navigation
Menu ItemSub-itemsStatus
## Dashboard—⚠️ (Most widgets work, but Documents/Service/Warranty queries have no data)
VehiclesBrowse Available Vehicles✅
My SalesSale Details · Contract · Insurance✅
PaymentsPayment History · Amortization Schedule✅
DocumentsOR, CR, Warranty Cert, Contracts❌
ServiceMy Bookings · Book a Service❌
WarrantyMy Claims · Submit Claim❌
InquiriesMy Inquiries · New Inquiry✅
NotificationsInbox✅
ProfileEdit Profile · Preferences✅
## 6.1 Customer Dashboard
WidgetData Source
Next Payment DueMIN(amortization.due_date) WHERE status=unpaid AND loan=mine
Next Payment Amountamortization.total_due for that row
Active Sales CountCOUNT sales WHERE customer_id=me AND status=active
Open InquiriesCOUNT inquiries WHERE user_id=me AND status!=closed
Unread NotificationsCOUNT notifications WHERE user_id=me AND is_read=0
## Recent Documents
SELECT documents WHERE sale.customer_id=me ORDER BY created_at
## DESC LIMIT 3
## 6.2 Vehicle Browse
-   Same public vehicle listing: grid cards with photo, brand, model, year, price, fuel type.

AutoMatik — UI Requirements  |  Page 16CONFIDENTIAL — For Internal Use Only
-   Filters: brand, model, fuel_type, transmission, price range slider.
-   Vehicle detail page: full photo carousel, all specs_json fields, inquiry button.
## 6.3 My Sales & Contracts
-   Sales list: vehicle photo, brand + model, sale_date, selling_price, payment_type badge, sale
status badge.
-   Sale detail accordion: contract status + download link, insurance info card, linked documents.
## 6.4 Loans & Amortization
-   Loan summary card: loan_amount, interest_rate, term_months, monthly_amortization,
bank_name, bank_approval_status badge.
-   Amortization table: month #, due_date, principal, interest, total_due, running_balance, status
badge (color-coded).
-   Progress bar: % of total loan paid vs remaining.
## 6.5 Payment History
-   Table: payment_date, amount_paid, payment_method badge, reference number, linked schedule
month.
-   Summary totals: total paid, total remaining balance.
## 6.6 My Documents  ❌ Planned
-   Grid of document cards: icon by document_type, label, date uploaded, 'View / Download' button.
-   Only shows is_accessible=1 records.
-   Document types: OR, CR, warranty_cert, amortization_schedule, sales_contract, other.
## 6.7 Service Bookings  ❌ Planned
FieldTypeDB Column / Source
SlotCalendar/Dropdownservice_slots WHERE is_available=1
Booking TypeSelectservice_bookings.booking_type (test_drive / maintenance / repair)
VehicleDropdownservice_bookings.vehicle_id (customer's purchased vehicle)
NotesTextareaservice_bookings.notes
Warranty ClaimDropdownservice_bookings.warranty_claim_id (optional, if repair)
-   Booking list: slot datetime, booking_type, vehicle, status badge, cancel button (if pending).
## 6.8 Warranty Claims  ❌ Planned
FieldTypeDB Column
SaleDropdownwarranty_claims.sale_id (customer's sales)

AutoMatik — UI Requirements  |  Page 17CONFIDENTIAL — For Internal Use Only
FieldTypeDB Column
VehicleAuto-fillwarranty_claims.vehicle_id (from sale)
Claim TypeSelectwarranty_claims.claim_type (repair / replacement / refund)
DescriptionTextareawarranty_claims.description
-   Claims list: claim_id, claim_type badge, status badge, submitted_at, resolution (if resolved).
## 6.9 My Inquiries
-   Inquiry list: vehicle, message preview, status badge, created_at, assigned agent name.
-   Submit new inquiry: same form as landing page inquiry, vehicle pre-selectable.
## 6.10 Notifications
-   Notification list: title, message, channel badge (in_app / email / sms), is_read indicator,
created_at, mark-read button.
-   Mark all read button in list header.
## 6.11 Profile Settings
FieldTypeDB Column
Full NameTextuser_profile.full_name
Phone NumberTeluser_profile.phone_number
AddressTextuser_profile.address
City / Province / ZIPTextuser_profile.city / province / zip_code
Date of BirthDateuser_profile.date_of_birth
GenderSelectuser_profile.gender
Profile PictureFile Uploaduser_profile.profile_picture_url
Preferred ContactSelectcustomer_details.preferred_contact_method
Preferred PaymentSelectcustomer_details.preferred_payment_method
Change PasswordPasswordusers.hashed_password (via PUT /profile/password)

AutoMatik — UI Requirements  |  Page 18CONFIDENTIAL — For Internal Use Only
## 7. Global Components
## 7.1 Authentication Screens
-   Login Page: email + password fields, 'Forgot Password' link, submit button. Redirect by role after
login.
-   Forgot Password: email input → trigger POST /auth/forgot-password → success message.
-   Reset Password: new password + confirm password → POST /auth/reset-password (token from
URL param).
-   Email Verification: landing page for /auth/verify-email?token=... → success/error state.
## 7.2 Error & Empty States
-   404 Page: 'Page not found' with back-to-dashboard button.
-   403 Page: 'Access denied' — shown when role check fails.
-   Empty Tables: illustrated empty state with action CTA per context.
-   API Error Toast: shown on 4xx/5xx responses with short message.
7.3 Shared UI Components
ComponentUsage
DataTableAll list views — search, sort, paginate, export
StatusBadgeColored chip for enum status fields across all tables
ConfirmModalDestructive action confirmation (delete, cancel, paid)
FileUploadDocument and photo upload with preview
CurrencyInputn-prefixed decimal input with comma formatting
DatePickerISO date picker for all date/datetime fields
NotificationBellTop-bar bell with unread count badge + dropdown
AvatarDropdownUser avatar, name, role, logout option
SidebarNavCollapsible role-specific navigation
SearchableDropdownVehicle, customer, agent, inquiry selectors
JsonDiffViewerAudit logs old vs new value side-by-side
AmortizationTableMonth-by-month breakdown with status indicators
PaymentCalculatorClient-side installment estimation widget
ChatbotWidgetFloating chat drawer (landing + logged-in views)

AutoMatik — UI Requirements  |  Page 19CONFIDENTIAL — For Internal Use Only
- Data Field Reference by Portal
Quick-reference table mapping every primary data entity to its portal visibility, showing which fields are
displayed vs editable per role.
EntityAdminAgentCustomerPublic     Status
usersView + EditOwn onlyOwn only—     ✅
user_profileView + Edit allOwn onlyOwn only—     ✅
agent_detailsView + EditView own——     ✅
customer_detailsView + Edit—View + Edit own—     ✅
vehiclesFull CRUD—View onlyView only     ✅
vehicle_photosUpload + Delete——View only     ✅
suppliersFull CRUD———     ✅
suppliesFull CRUD———     ❌
inquiriesFull CRUD + AssignOwn assignedOwn onlySubmit only     ✅
chatbot_logsView all—Own sessionOwn session     ❌
salesFull CRUD—View own—     ✅
sales_contractsFull CRUDView assignedView own—     ✅
loan_detailsFull CRUD—View own—     ✅
amortization_scheduleView + Edit—View own—     ✅
paymentsRecord + View—View own—     ✅
agent_commissionsView + Mark PaidView own——     ❌
agent_tasks—Full CRUD own——     ❌
documentsFull CRUDView linkedView own (accessible)—     ❌
insurance_recordsFull CRUD—View own—     ✅
service_slotsFull CRUD——View available     ❌
service_bookingsView + Confirm—Create + Cancel own—     ❌
warranty_claimsReview + Resolve—Submit + View own—     ❌
notificationsBroadcastOwn onlyOwn only—     ⚠️
audit_logsView all———     ⚠️
system_settingsFull CRUD———     ❌

AutoMatik — UI Requirements  |  Page 20CONFIDENTIAL — For Internal Use Only
Note: This document is to be used as the primary specification handoff from the SA/DB teams to the UI/UX and FS
(Frontend Systems) teams. Any deviations require written approval and must be reflected in the next document
revision.

---

## Appendix A — Backend Implementation Status

The table below shows which features documented in this UI requirements doc have corresponding backend API endpoints implemented as of June 2026.

| # | Feature | Section(s) | DB Table Exists | Backend API | Priority |
|---|---------|-----------|----------------|-------------|----------|
| 1 | Auth (login, logout, register, change password, forgot/reset password) | 7.1 | ✅ | ✅ | — |
| 2 | User Management (list, get, update, delete users) | 4.2 | ✅ | ✅ | — |
| 3 | Agent Management (list, update commission rate) | 4.2 | ✅ | ✅ | — |
| 4 | Customer Management (list, get, update) | 4.2 | ✅ | ✅ | — |
| 5 | Vehicle CRUD + Search + Photos | 4.3, 6.2 | ✅ | ✅ | — |
| 6 | Vehicle Status Transitions | 4.3 | ✅ | ✅ | — |
| 7 | Low Stock Report | 4.3 | ✅ | ✅ | — |
| 8 | **Supplies / Parts Inventory** | 4.11 | ✅ | ❌ Planned | Medium |
| 9 | Supplier CRUD | 4.11 | ✅ | ✅ | — |
| 10 | Inquiry Submit (public) | 3.3, 6.9 | ✅ | ✅ | — |
| 11 | Inquiry Assign (admin) | 4.4 | ✅ | ✅ | — |
| 12 | Inquiry Resolve (agent) | 4.4, 5.2 | ✅ | ✅ | — |
| 13 | Inquiry Close (admin) | 4.4 | ✅ | ✅ | — |
| 14 | **Chatbot** | 3.2 | ✅ | ❌ Planned | Low |
| 15 | **Chatbot Logs View** | 4.4 | ✅ | ❌ Planned | Low |
| 16 | Sales CRUD | 4.5, 6.3 | ✅ | ✅ | — |
| 17 | Contracts (create, sign) | 4.5 | ✅ | ✅ | — |
| 18 | Insurance (create, update) | 4.5 | ✅ | ✅ | — |
| 19 | Loans (create, approve/reject) | 4.6, 6.4 | ✅ | ✅ | — |
| 20 | Amortization Schedule (generate, update status, overdue) | 4.6 | ✅ | ✅ | — |
| 21 | Amortization Recompute | 4.6 | ✅ | ✅ | — |
| 22 | Payments (record, list, summary) | 4.7, 6.5 | ✅ | ✅ | — |
| 23 | **Commissions — Agent self-service view** | 5.4 | ✅ | ❌ Planned | Medium |
| 24 | **Commissions — Admin mark as paid** | 4.1 | ✅ | ❌ Planned | Medium |
| 25 | **Agent Tasks CRUD** | 5.3 | ✅ | ❌ Planned | Medium |
| 26 | **Service Slots Management** | 4.8, 3.2 | ✅ | ❌ Planned | Medium |
| 27 | **Service Bookings** | 4.8, 6.7 | ✅ | ❌ Planned | Medium |
| 28 | **Warranty Claims** | 4.9, 6.8 | ✅ | ❌ Planned | Medium |
| 29 | **Documents (upload, list, download)** | 4.10, 6.6 | ✅ | ❌ Planned | Medium |
| 30 | Profile (get, update own) | 6.11 | ✅ | ✅ | — |
| 31 | Change Password | 6.11 | ✅ | ✅ | — |
| 32 | Notifications (list unread, mark read) | 6.10 | ✅ | ✅ | — |
| 33 | **Notification Broadcast (admin)** | 4.12 | ✅ | ❌ Planned | Low |
| 34 | Audit Logs (basic list) | 4.13 | ✅ | ⚠️ Partial | Low |
| 35 | **Audit Logs (filtering, pagination, diff viewer)** | 4.13 | ✅ | ❌ Planned | Low |
| 36 | **System Settings** | 4.14 | ✅ | ❌ Planned | Low |
| 37 | Email Verification | 7.1 | ✅ | ✅ | — |
| 38 | Email Notifications (welcome, inquiry, sale, payment, loan, warranty, booking, password reset) | — | ✅ | ✅ | —