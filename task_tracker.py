import uuid
import datetime
import json

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
    
    
        
        
    

