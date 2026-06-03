# blueprint
from flask import Blueprint

# validators
from validators.middleware import (
    logged_in_required,
    role_required
)

# import functions from agentController
from controllers.agentController import (
    getDashboard,
    getInquiries,
    getTasks,
    createTask,
    updateTask,
    deleteTask
)

agent_bp = Blueprint("agent_portal", __name__)

@agent_bp.route("/agent/dashboard", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_dashboard():
    return getDashboard()

@agent_bp.route("/agent/inquiries", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_inquiries():
    return getInquiries()

@agent_bp.route("/agent/tasks", methods=["GET"])
@logged_in_required
@role_required("agent")
def get_tasks():
    return getTasks()

@agent_bp.route("/agent/tasks", methods=["POST"])
@logged_in_required
@role_required("agent")
def create_tasks():
    return createTask()

@agent_bp.route("/agent/tasks/<int:task_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def update_task(task_id):
    return updateTask(task_id)

@agent_bp.route("/agent/tasks/<int:task_id>", methods=["DELETE"])
@logged_in_required
@role_required("agent")
def delete_task(task_id):
    return deleteTask(task_id)



