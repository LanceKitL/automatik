from conn import connection
from flask import jsonify, request

#GET - Agent tasks
def getMyTasks(agent_id):
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agent_tasks WHERE agent_id = %s", (agent_id,))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": tasks})

#CREATE - Agent Tasks
def createTask():
    data = request.get_json()
    agent_id = data["agent_id"]
    inquiry_id = data.get("inquiry_id",None)
    task_type = data.get("task_type",None)
    title = data["title"]
    due_date = data.get("due_date",None)
    status = data.get("status", "pending")
    notes = data.get("notes", None)
 
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO agent_tasks (agent_id, inquiry_id, task_type, title, due_date, status, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (agent_id, inquiry_id, task_type, title, due_date, status, notes)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Task created successfully!"})

# GET - Agent tasks
def getTaskById(task_id):
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agent_tasks WHERE task_id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({"data": task})
 
# UPDATE - Agent tasks
def updateTask(task_id):
    data = request.get_json()
    agent_id = data["agent_id"]
    inquiry_id = data.get("inquiry_id",None)
    task_type = data.get("task_type",None)
    title = data["title"]
    due_date = data.get("due_date",None)
    status = data.get("status", "pending")
    notes = data.get("notes", None)
 
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "UPDATE agent_tasks SET agent_id=%s, inquiry_id=%s, task_type=%s, title=%s, due_date=%s, status=%s, notes=%s  WHERE task_id = %s",
        (agent_id, inquiry_id, task_type, title, due_date, status, notes, task_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Task {task_id} updated successfully!"})
 
# DELETE - Agent tasks
def deleteTask(task_id):
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM agent_tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Task {task_id} deleted successfully!"})
 
