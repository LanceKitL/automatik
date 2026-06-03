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
    getInquiries,
    getTasks,
    createTask,
    updateTask,
    deleteTask,
    # ADMIN 
    getCommissions,
    getCommissionsAdmin,
    payCommission,
    agentPerformance
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