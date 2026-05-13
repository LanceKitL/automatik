from flask import Flask, jsonify
from controllers.agent_tasks import getMyTasks, createTask, getTaskById, updateTask, deleteTask
from controllers.documents import uploadContract, getDocumentsBySale, uploadDocument
from controllers.insurance import  getInsuranceBySale, addInsurance

app = Flask(__name__)
app.secret_key = "super_secret_ultra_key"
    

#AGENT TASKS

#GET - AGENT
@app.route("/get_agent/<agent_id>", methods=["GET"])
def get_my_tasks(agent_id):
    return getMyTasks(agent_id)
 
 #POST - CREATE AGENT TASK
@app.route("/create_agent_tasks", methods=["POST"])
def create_task():
    return createTask()
 
 #GET - TASK ID
@app.route("/get_task_id/<int:task_id>", methods=["GET"])
def get_task(task_id):
    return getTaskById(task_id)
 
 #PUT - UPDATE TASK
@app.route("/update_task/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    return updateTask(task_id)
 
 #DELETE -  DELETE TASK
@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    return deleteTask(task_id)

#DOCUMENTS

#POST - UPLOAD CONTRACT
@app.route("/upload_contract/<int:sale_id>/", methods=["POST"])
def upload_contract(sale_id):
    return uploadContract(sale_id)
 
#GET - GET DOCUMENT
@app.route("/get_document/<int:sale_id>/", methods=["GET"])
def get_documents(sale_id):
    return getDocumentsBySale(sale_id)
 
 #POST - UPLOAD DOCUMENT
@app.route("/upload_document/<int:sale_id>/", methods=["POST"])
def upload_document(sale_id):
    return uploadDocument(sale_id)

#INSURANCE

#GET - GET INSURANCE
@app.route("/get_insurance/<int:sale_id>/", methods=["GET"])
def get_insurance(sale_id):
    return getInsuranceBySale(sale_id)
 
 #POST - ADD INSURANCE
@app.route("/add_insurance/<int:sale_id>/", methods=["POST"])
def add_insurance(sale_id):
    return addInsurance(sale_id)


if __name__ == "__main__":
    app.run(debug=True)