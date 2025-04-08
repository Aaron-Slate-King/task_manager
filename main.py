from getpass import getpass
import sqlite3
import datetime

class Database:
    def __init__(self, db_name='task_manager.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.setup_database()
    
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        # Create users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            streak INTEGER DEFAULT 0
        )
        ''')
        
        # Create tasks table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            completion_status TEXT,
            due_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        self.connection.commit()
    
    def add_user(self, username, password):
        """Add a new user to the database"""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, streak) VALUES (?, ?, ?)",
                (username, password, 0)
            )
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Username already exists
            return None
    
    def authenticate_user(self, username, password):
        """Verify user credentials"""
        self.cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = self.cursor.fetchone()
        return user[0] if user else None
    
    def get_user_details(self, user_id):
        """Get user details by ID"""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def add_task(self, user_id, title, description, priority, completion_status, due_date):
        """Add a new task to the database"""
        self.cursor.execute(
            "INSERT INTO tasks (user_id, title, description, priority, completion_status, due_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, title, description, priority, completion_status, due_date)
        )
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_user_tasks(self, user_id, completion_status=None):
        """Get all tasks for a specific user"""
        if completion_status:
            self.cursor.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND completion_status = ?",
                (user_id, completion_status)
            )
        else:
            self.cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()
    
    def get_task(self, task_id):
        """Get a specific task by ID"""
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return self.cursor.fetchone()
    
    def update_task(self, task_id, title=None, description=None, priority=None, completion_status=None, due_date=None):
        """Update task details"""
        current_task = self.get_task(task_id)
        if not current_task:
            return False
        
        # Use current values if new ones aren't provided
        title = title if title is not None else current_task[2]
        description = description if description is not None else current_task[3]
        priority = priority if priority is not None else current_task[4]
        completion_status = completion_status if completion_status is not None else current_task[5]
        due_date = due_date if due_date is not None else current_task[6]
        
        self.cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, completion_status = ?, due_date = ? WHERE id = ?",
            (title, description, priority, completion_status, due_date, task_id)
        )
        self.connection.commit()
        return True
    
    def delete_task(self, task_id):
        """Delete a task by ID"""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Close the database connection"""
        self.connection.close()


class User:
    def __init__(self, username, password, user_id=None, streak=0):
        self.id = user_id
        self.username = username
        self.password = password
        self.streak = streak


class Task:
    def __init__(self, title, description, priority, completion_status, due_date, task_id=None, user_id=None):
        self.id = task_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completion_status = completion_status
        self.due_date = due_date


def user_access_options(db):
    user_access_choice = input("Enter your choice (1 or 2): ")
    if user_access_choice == "1":
        user_id = sign_in_input(db)
        if user_id:
            user = db.get_user_details(user_id)
            username = user[1]  # Index 1 corresponds to username in the database
            print(f"Hello {username}, here are your current uncompleted tasks:")
            display_user_tasks(db, user_id, "incomplete")
            return user_id
        else:
            print("Invalid username or password. Please try again.")
            return None
    elif user_access_choice == "2":
        user_id = create_account_input(db)
        if user_id:
            print(f"Account created successfully! Your user ID is {user_id}")
            return user_id
        else:
            print("Username already exists. Please try another username.")
            return None
    else:
        print("Invalid choice. Please try again.")
        return None


def sign_in_input(db):
    received_username = input("Please enter your username: ")
    received_password = getpass("Please enter your password: ")
    
    return db.authenticate_user(received_username, received_password)


def create_account_input(db):
    username = input("Please create a username: ")
    password = input("Please create a password: ")
    
    return db.add_user(username, password)


def display_user_tasks(db, user_id, filter_status=None):
    tasks = db.get_user_tasks(user_id, filter_status)
    if tasks:
        print("\nYour Tasks:")
        for i, task in enumerate(tasks, 1):
            # SQLite returns data as tuples with indices corresponding to table columns
            # (id, user_id, title, description, priority, completion_status, due_date)
            print(f"{i}. Title: {task[2]}, Priority: {task[4]}, Status: {task[5]}, Due: {task[6]}")
    else:
        print("No tasks found.")
    return tasks


def get_task_details():
    title = input("Please enter the title of your task: ")
    description = input("Please enter the description of your task: ")
    
    while True:
        priority = input("Please enter the priority of your task (low/medium/high): ").lower()
        if priority in ['low', 'medium', 'high']:
            break
        print("Invalid priority level. Please enter low, medium, or high.")
    
    while True:
        completion_status = input("Please enter the completion status of your task:\n1. not started\n2. in progress\n3. completed\nChoice: ")
        if completion_status == "1":
            completion_status = "not started"
            break
        elif completion_status == "2":
            completion_status = "in progress"
            break
        elif completion_status == "3":
            completion_status = "completed"
            break
        print("Invalid option. Please choose 1, 2, or 3.")
    
    while True:
        try:
            due_date = input("Please enter the due date of your task (YYYY-MM-DD): ")
            # Validate date format
            datetime.datetime.strptime(due_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    return title, description, priority, completion_status, due_date


def main():
    db = Database()
    
    print("*****************************************")
    print("*Hello, welcome to Aaron's Task Manager!*")
    print("*****************************************")
    print("Please type '1' to sign in or type '2' to create an account")
    
    user_id = user_access_options(db)
    
    if user_id:
        main_loop = True
        while main_loop:
            print("\nWhat would you like to do?")
            user_option_select_choice = input("Please input a number:\n1. View my tasks\n2. Edit a task\n3. Create a new task\n4. Delete a task\n5. Log out\nChoice: ")
            
            if user_option_select_choice == "1":
                filter_option = input("Filter tasks by status?\n1. All tasks\n2. Not started\n3. In progress\n4. Completed\nChoice: ")
                filter_status = None
                if filter_option == "2":
                    filter_status = "not started"
                elif filter_option == "3":
                    filter_status = "in progress"
                elif filter_option == "4":
                    filter_status = "completed"
                
                tasks = display_user_tasks(db, user_id, filter_status)
                if tasks:
                    task_view_choice = input("Enter task number to view details (or 0 to go back): ")
                    try:
                        task_index = int(task_view_choice) - 1
                        if 0 <= task_index < len(tasks):
                            task = tasks[task_index]
                            print("\nTask Details:")
                            print(f"Title: {task[2]}")
                            print(f"Description: {task[3]}")
                            print(f"Priority: {task[4]}")
                            print(f"Status: {task[5]}")
                            print(f"Due Date: {task[6]}")
                    except ValueError:
                        print("Invalid selection")
            
            elif user_option_select_choice == "2":
                tasks = display_user_tasks(db, user_id)
                if tasks:
                    try:
                        edit_task_choice = int(input("Enter task number to edit (or 0 to go back): "))
                        if 1 <= edit_task_choice <= len(tasks):
                            task = tasks[edit_task_choice - 1]
                            task_id = task[0]
                            
                            print("\nUpdate Task (leave blank to keep current value)")
                            new_title = input(f"Title [{task[2]}]: ") or None
                            new_description = input(f"Description [{task[3]}]: ") or None
                            
                            new_priority = None
                            priority_input = input(f"Priority [{task[4]}] (low/medium/high): ").lower()
                            if priority_input in ['low', 'medium', 'high']:
                                new_priority = priority_input
                            
                            new_status = None
                            status_choice = input(f"Status [{task[5]}]:\n1. not started\n2. in progress\n3. completed\nChoice: ")
                            if status_choice == "1":
                                new_status = "not started"
                            elif status_choice == "2":
                                new_status = "in progress"
                            elif status_choice == "3":
                                new_status = "completed"
                            
                            new_due_date = None
                            due_date_input = input(f"Due Date [{task[6]}] (YYYY-MM-DD): ")
                            if due_date_input:
                                try:
                                    datetime.datetime.strptime(due_date_input, '%Y-%m-%d')
                                    new_due_date = due_date_input
                                except ValueError:
                                    print("Invalid date format. Keeping original due date.")
                            
                            if db.update_task(task_id, new_title, new_description, new_priority, new_status, new_due_date):
                                print("Task updated successfully!")
                            else:
                                print("Failed to update task.")
                    except ValueError:
                        print("Invalid selection")
            
            elif user_option_select_choice == "3":
                print("\nCreate a new task:")
                title, description, priority, completion_status, due_date = get_task_details()
                
                task_id = db.add_task(user_id, title, description, priority, completion_status, due_date)
                if task_id:
                    print(f"Task '{title}' created successfully!")
                else:
                    print("Failed to create task.")
            
            elif user_option_select_choice == "4":
                tasks = display_user_tasks(db, user_id)
                if tasks:
                    try:
                        delete_task_choice = int(input("Enter task number to delete (or 0 to go back): "))
                        if 1 <= delete_task_choice <= len(tasks):
                            task_id = tasks[delete_task_choice - 1][0]
                            confirm = input(f"Are you sure you want to delete '{tasks[delete_task_choice - 1][2]}'? (y/n): ").lower()
                            if confirm == 'y':
                                if db.delete_task(task_id):
                                    print("Task deleted successfully!")
                                else:
                                    print("Failed to delete task.")
                    except ValueError:
                        print("Invalid selection")
            
            elif user_option_select_choice == "5":
                print("Goodbye and see you soon!")
                main_loop = False
            
            else:
                print("Invalid choice. Please try again.")
    
    db.close()


if __name__ == "__main__":
    main()