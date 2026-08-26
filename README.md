# CLI Task Tracker

A Object-Oriented command-line task management application build in python. 
Features JSON persistence, input validation, data-based filtering, and file-corruption recovery

## Prerequisites

- Python 3.8 or higher installed on your system

## Usage Guide

Run the tool from your terminal using 'python task_tracker.py [command] [arguments]'

### 1. add a task
Add a task with a required priority ('low', 'medium', 'high') and an optional description and due-date:

```bash
python task_tracker.py add "Buy groceries" --priority high --due-date 2026-08-30 --description "milk, eggs, bread"
```
### 2. List tasks
View pending tasks (default)

```bash
python task_tracker.py list
```

View completed tasks

```bash
python task_tracker.py list --status Completed
```

View all tasks regardless of status

```bash
python task_tracker.py list --all
```

Filter by due date

```bash
python task_tracker.py list --due-date Today --priority high
```

### 3. Show task details
View full details of a specific task using its 8-character ID:

```bash
python task_tracker.py show [ID]
```

### 4. Edit a task
Update specific fields of an existing task using named flags

```bash
python task_tracker.py edit [ID] --priority medium --name "Buy organic groceries"
```

### 5. Complete a task
Mark a task as completed

```bash
python task_tracker.py complete [ID]
```

## Error Handling

If tasks.json is malformed, the app renames itself to tasks_corrupted_YYYMMDDHH.json, prints a warning and initialises a fresh list
File I/O errors are caught at the CLI layer to prevent large stack traces



