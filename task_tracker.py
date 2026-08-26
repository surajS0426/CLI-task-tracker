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
            return True
        return False
    
    def mark_task_completed(self, task_id):
        return self.update_task_status(task_id, "Completed")
        
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
        elif due_date == "Today":
            results = [task for task in results if task.due_date and task.due_date == today]
        elif due_date == "Week":
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
            raise RuntimeError(f"Error: The tasks file '{filename}' is corrupted. A backup has been created as '{backup_filename}'. Please check the backup file for your tasks.")
            
    
import argparse

def main():
    manager = TaskManager()
    try:
        manager.load_tasks_from_file('tasks.json')
    except RuntimeError as e:
        print(f"Warning: {e}")
    except OSError:
        print("Error: Unable to access the tasks file. Please check file permissions.")
        return
        
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("name", type=str, help="Name of the task")
    add_parser.add_argument("--priority", type=str, choices=["low", "medium", "high"], required=True, help="Priority of the task")
    add_parser.add_argument("--due-date", type=str, help="Due date of the task in YYYY-MM-DD format")
    add_parser.add_argument("--description", type=str, help="Description of the task")
    
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", type=str, choices=["Completed", "Pending"], help="Filter tasks by status")
    list_parser.add_argument("--priority", type=str, choices=["low", "medium", "high"], help="Filter tasks by priority")
    list_parser.add_argument("--due-date", type=str, choices=["Overdue", "Today", "Week"], help="Filter tasks by due date")
    list_parser.add_argument("--all", action="store_true", help="List all tasks regardless of status")
    
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("task_id", type=str, help="ID of the task to mark as completed")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=str, help="ID of the task to delete")
    
    show_parser = subparsers.add_parser("show", help="Show details of a task")
    show_parser.add_argument("task_id", type=str, help="ID of the task to show details for")
    
    edit_parser = subparsers.add_parser("edit", help="Edit a task")
    edit_parser.add_argument("task_id", type=str, help="ID of the task to edit")
    edit_parser.add_argument("--name", type=str, help="New name of the task")
    edit_parser.add_argument("--priority", type=str, choices=["low", "medium", "high"], help="New priority of the task")
    edit_parser.add_argument("--due-date", type=str, help="New due date of the task in YYYY-MM-DD format")
    edit_parser.add_argument("--description", type=str, help="New description of the task")
    
    
    def safe_input():
        try:
            manager.save_tasks_to_file('tasks.json')
            return True
        except OSError:
            print("Error: could not save tasks to disk. Please check file permissions")
            return False

    args = parser.parse_args()
    
    if args.command == "add":
        final_due_date = None
        if args.due_date:
            try:
                final_due_date = datetime.date.fromisoformat(args.due_date)
            except ValueError:
                print("Error: Invalid due date format. Please use YYYY-MM-DD.")
                return
        if args.name.strip() == "":
            print("Error: Task name cannot be empty.")
            return
        new_task = Task(name=args.name, priority=args.priority, due_date=final_due_date, description=args.description)
        manager.add_task(new_task)
        if safe_input():
            print(f"Task '{args.name}' added successfully.")
    
    elif args.command == "list":
        if args.all:
            tasks = manager.list_tasks()
        else:
            tasks = manager.list_tasks(status=args.status, priority=args.priority, due_date=args.due_date)
        if not tasks:
            print("No tasks found.")
        else:
            for task in tasks:
                due_date_str = task.due_date.isoformat() if task.due_date else "No due date"
                print(f"ID: {task.task_id}, Name: {task.name}, Priority: {task.priority}, Due Date: {due_date_str}, Status: {task.status}")
    
    elif args.command == "complete":
        success = manager.mark_task_completed(args.task_id)
        if success:
            manager.save_tasks_to_file('tasks.json')
            print(f"Task with ID '{args.task_id}' marked as completed.")
        else:
            print(f"Error: Task with ID '{args.task_id}' not found.")

    elif args.command == "delete":
        task_to_delete = manager.get_task(args.task_id)
        
        if not task_to_delete:
            print(f"Error: Task with ID '{args.task_id}' not found.")
        else:
            confirm = input(f"Are you sure you want to delete the task '{task_to_delete.name}'? (y/n): ")
            if confirm.lower() == 'y':
                manager.remove_task(args.task_id)
                if safe_input():
                    print(f"Task with ID '{args.task_id}' deleted successfully.")
            else:
                print("Task deletion canceled.")

    elif args.command == "show":
        task = manager.get_task(args.task_id)
        if task:
            due_date_str = task.due_date.isoformat() if task.due_date else "No due date"
            description_str = task.description if task.description else "No description"
            print(f"ID: {task.task_id}\nName: {task.name}\nDescription: {description_str}\nPriority: {task.priority}\nDue Date: {due_date_str}\nStatus: {task.status}")
        else:
            print(f"Error: Task with ID '{args.task_id}' not found.")
            
    elif args.command == "edit":
        task_to_edit = manager.get_task(args.task_id)
        if not task_to_edit:
            print(f"Error: Task with ID '{args.task_id}' not found.")
            return
        
        # Update task attributes if new values are provided
        updates = {}
        if args.name is not None:
            if args.name.strip() == "":
                print("Error: Task name cannot be empty.")
                return
            updates['name'] = args.name
        
        if args.priority is not None:
            updates['priority'] = args.priority
            
        if args.due_date is not None:
            try:
                updates['due_date'] = datetime.date.fromisoformat(args.due_date)
            except ValueError:
                print("Error: Invalid due date format. Please use YYYY-MM-DD.")
                return
        if args.description is not None:
            updates['description'] = args.description
            
        if not updates:
            print("No updates provided. Task remains unchanged.")
            return
        
        manager.update_task(args.task_id, **updates)
        if safe_input():
            print(f"Task with ID '{args.task_id}' updated successfully.")
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()