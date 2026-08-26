from time import time
import uuid
import datetime
import json
import os, pathlib


class Task:
    
    def __init__(self, name, priority, description=None, due_date=None, status="Pending", task_id=None):
        self.name = name
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = status  # Default status is "Pending"
        self.task_id = task_id if task_id is not None else uuid.uuid4().hex[:8]  # Generate a unique identifier for the task
        
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status
        }
        

class TaskManager:
    
    def __init__(self):
        self.tasks = {}
        
    def add_task(self, task):
        self.tasks[task.task_id] = task
        
    def remove_task(self, task_id):
        self.tasks.pop(task_id, None)
        
    def update_task(self, task_id, **kwargs):
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
                        
    def get_task(self, task_id):
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id, new_status):
        task = self.get_task(task_id)
        if task:
            task.status = new_status
    
    def mark_task_completed(self, task_id):
        self.update_task_status(task_id, "Completed")
        
    def list_tasks(self, status=None, priority=None, due_date=None):
        results = list(self.tasks.values())
        today = datetime.date.today()
        
        if status == "Completed":
            results = [task for task in results if task.status == "Completed"]
        else:
            results = [task for task in results if task.status == "Pending"]
        if priority is not None:
            results = [task for task in results if task.priority == priority]
        if due_date == "Overdue":
            results = [task for task in results if task.due_date and task.due_date < today]
        elif due_date == "Due Today":
            results = [task for task in results if task.due_date and task.due_date == today]
        elif due_date == "Due This Week":
            week_start = today - datetime.timedelta(days=today.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            results = [task for task in results if task.due_date and week_start <= task.due_date <= week_end]

        return results
    
    
    def save_tasks_to_file(self, filename):
        tasks = [task.to_dict() for task in self.tasks.values()]
        with open(filename, 'w') as file:
            json.dump(tasks, file)
            
    def load_tasks_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                tasks_data = json.load(file)
                for task_data in tasks_data:
                    task = Task(
                        name=task_data["name"],
                        description=task_data.get("description"),
                        priority=task_data["priority"],
                        due_date=datetime.datetime.fromisoformat(task_data["due_date"]).date() if task_data.get("due_date") else None,
                        status=task_data.get("status", "Pending"),
                        task_id=task_data["task_id"]
                    )
                    self.add_task(task)
        except FileNotFoundError:
            pass  # If the file doesn't exist, we simply start with an empty task list
        except json.JSONDecodeError:
            backup_filename = f"tasks_corrupted_{int(time.time())}.json"
            os.rename(filename, backup_filename)
            
            print(f"Error: The file '{filename}' is corrupted. It has been renamed to '{backup_filename}'. Starting with an empty task list.")
            
    

