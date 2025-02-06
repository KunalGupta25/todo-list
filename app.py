from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
import firebase_admin
from firebase_admin import db
import json
import os

app = Flask(__name__)

cred_obj = firebase_admin.credentials.Certificate('/etc/secrets/key.json')
firebase_admin.initialize_app(cred_obj, {'databaseURL': 'https://todolist-acfee-default-rtdb.firebaseio.com/'})

todo_ref = db.reference('todos')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task = request.form.get("task")
        desc = request.form.get("desc")
        date = datetime.utcnow().strftime("%Y-%m-%d %I:%M %p")  # Example: 2025-02-03 04:30 PM

        if task and desc:
            new_task_ref = todo_ref.push()
            new_task_ref.set({"task": task, "desc": desc, "date": date, "status": False})
            # print(f"Added task: {task}, description: {desc}")  # Debugging log
            return redirect('/')  # Redirect to prevent resubmission
    
    tasks = todo_ref.get() or {}
    # print(f"Retrieved tasks: {tasks}")  # Debugging log
    return render_template("index.html", tasks=tasks)

@app.route("/toggle_status/<task_id>", methods=["POST"])
def toggle_status(task_id):
    task_ref = db.reference(f"todos/{task_id}")  # Corrected path to reference the task
    task_data = task_ref.get()  # Fetch task details
    
    if not task_data:
        return jsonify({"error": "Task not found"}), 404
    
    current_status = task_data["status"]
    new_status = not current_status  # Toggle status
    
    task_ref.update({"status": new_status})  # Update in Firebase

    return jsonify({"success": True, "new_status": new_status, "status_icon": "✅" if new_status else "❌"})

@app.route("/about")
def about_me():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
