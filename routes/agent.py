# blueprint
from flask import Blueprint

# validators
from validators.middleware import (
    logged_in_required,
    role_required
)

# import functions from agentController
from controllers.agentController import (
    # AGENT
    getDashboard,
    getTestDrives,
    getInquiries,
    getTasks,
    createTask,
    updateTask,
    deleteTask,
    agentSubmitInquiry,
    agentBookTestDrive,
    # ADMIN 
    getCommissions,
    getCommissionsAdmin,
    payCommission,
    agentPerformance
)

from controllers.vehicleController import (
    getVehicles,
    showVehicle,
)

from controllers.serviceController import (
    updateBookingStatusHandler,
    assignToSelfHandler,
)

agent_bp = Blueprint("agent_portal", __name__)

@agent_bp.route("/agent/dashboard", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_dashboard():
    """
    Fetch all the dashboard information | data
    """
    return getDashboard()

@agent_bp.route("/agent/test-drives", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_test_drives():
    """List test drive bookings for the agent portal."""
    return getTestDrives()

@agent_bp.route("/agent/test-drives/<int:booking_id>/assign", methods=["PUT"])
@logged_in_required
@role_required("agent")
def assign_test_drive(booking_id):
    """Self-assign a test drive booking."""
    return assignToSelfHandler(booking_id)

@agent_bp.route("/agent/test-drives/<int:booking_id>/confirm", methods=["PUT"])
@logged_in_required
@role_required("agent")
def confirm_test_drive(booking_id):
    """Confirm a test drive booking."""
    return updateBookingStatusHandler(booking_id, "confirmed")

@agent_bp.route("/agent/test-drives/<int:booking_id>/complete", methods=["PUT"])
@logged_in_required
@role_required("agent")
def complete_test_drive(booking_id):
    """Complete a test drive booking."""
    return updateBookingStatusHandler(booking_id, "completed")

@agent_bp.route("/agent/test-drives/<int:booking_id>/cancel", methods=["PUT"])
@logged_in_required
@role_required("agent")
def cancel_test_drive(booking_id):
    """Cancel a test drive booking."""
    return updateBookingStatusHandler(booking_id, "cancelled")

@agent_bp.route("/agent/inquiries", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_inquiries():
    """
    Fetch all the available inquiries for CURRENT LOGGED IN AGENT
    """
    return getInquiries()

@agent_bp.route("/agent/tasks", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_tasks():
    """
    This route fetch all the CURRENT LOGGED IN AGENT tasks
    """
    return getTasks()

@agent_bp.route("/agent/tasks", methods=["POST"])
@logged_in_required
@role_required("agent")
def create_tasks():
    """
    This route creates an agent task they can also BIND THE INQUIRY (OPTIONAL)
    
    this acts like a to do lists for agents.
    """
    return createTask()

@agent_bp.route("/agent/tasks/<int:task_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def update_task(task_id):
    """
        This route updates specific columns from agent task
        
        such as:
            - status
            - task_type
            - notes
            - due_date
    """
    return updateTask(task_id)

@agent_bp.route("/agent/tasks/<int:task_id>", methods=["DELETE"])
@logged_in_required
@role_required("agent")
def delete_task(task_id):
    """
    This routes completely DELETES agent_tasks
    """
    return deleteTask(task_id)

@agent_bp.route("/agent/commissions", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_commissions():
    """
    This route display all the commission/s of the CURRENT AGENT LOGGED IN.
    """
    return getCommissions()

@agent_bp.route("/agent/vehicles", methods=["GET"])
@logged_in_required
@role_required("agent")
def agent_vehicles():
    """GET /agent/vehicles
    List all available vehicles for walk-in browsing.
    """
    return getVehicles()


@agent_bp.route("/agent/vehicles/<int:vehicle_id>", methods=["GET"])
@logged_in_required
@role_required("agent")
def agent_vehicle_detail(vehicle_id):
    """GET /agent/vehicles/<vehicle_id>
    View details of a specific vehicle.
    """
    return showVehicle(vehicle_id)


@agent_bp.route("/agent/inquiries", methods=["POST"])
@logged_in_required
@role_required("agent")
def agent_create_inquiry():
    """POST /agent/inquiries
    Create an inquiry on behalf of a walk-in guest. Auto self-assigns.
    Body: { vehicle_id, message, guest_name, guest_email, guest_number? }
    """
    return agentSubmitInquiry()


@agent_bp.route("/agent/bookings", methods=["POST"])
@logged_in_required
@role_required("agent")
def agent_create_booking():
    """POST /agent/bookings
    Book a test drive for a walk-in guest.
    Body: { slot_id, vehicle_id, guest_name, guest_email }
    """
    return agentBookTestDrive()


#-------- ADMIN ROUTES -------- 
@agent_bp.route("/admin/commissions", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_commissions_admin():
    """ 
    This route displays all the commissions for admin portal
    
    this route can also handle searches for the ff fields:
    
    + agent_id [int]
    + is_paid [0,1]   
    
    sample usage: /admin/commissions?agent_id=2&is_paid=0 
    """
    return getCommissionsAdmin()


@agent_bp.route("/admin/commissions/<int:commission_id>/pay", methods=["PUT"])
def pay_commission(commission_id):
    """
    This route will set the is_paid to 1 (or true) and automatically adds a
    date when it was updated. 
    """
    return payCommission(commission_id) 

@agent_bp.route("/admin/agents/<int:agent_id>/performance")
def agent_performance(agent_id):
    """
    This route will display all the specific agent stats such as:
    - total sales
    - revenue 
    - commission total,
    - avg rate
    """
    return agentPerformance(agent_id)