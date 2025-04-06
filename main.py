from getpass import getpass
import sqlite3

username = "Aaron"
password = "Password"

id_count = 0
task_count = 1

users_dict = {}

task_dict = {0: "stuff"}

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.streak = 0

#Would it make sense to make the status an enum, since it needs to only be a few set values. I dont think it does because the GUI later on will only allow a few choices.
class Task:
    def __init__(self, title, description, priority, completion_status, due_date):
        self.title = title
        self.description = description
        self.priority = priority
        self.completion_status = completion_status
        self.due_date = due_date


def user_access_options():
    user_access_choice = input()
    if user_access_choice == "1":
        if sign_in_input():
            print(f"hello {username}, here are your current uncompleted tasks.\n{task_dict[0]}")

    elif user_access_choice == "2":
        create_account_input()


def sign_in_input():
    recieved_username = input("please enter your username: ")
    recieved_password = getpass("please enter your password: ")

    if recieved_username == username and recieved_password == password:
        return True
    else:
        return False


def create_account_input():
    global id_count
    username = input("Please create a username: ")
    password = input("Please create a password: ")

    new_user = User(username, password)
    users_dict[id_count] = new_user

    print(users_dict[0].name)

    assigned_id = id_count
    id_count += 1

    return assigned_id




def main():
    print("*****************************************")
    print("*hello, welcome to Aaron's Task Manager!*")
    print("*****************************************")
    print("Please type '1' to sign in or type '2' to create an account")

    #Begins the process of either signing in with an account or creating a new one
    user_access_options()

    main_loop = True
    while main_loop == True:
        user_option_select_choice = input("Please input a number:\n1. view my tasks\n2. edit a task\n3. create a new task\n4. log out")
        if user_option_select_choice == "1":
            task_view_choice = input(f"Which task would you like to view?\n{task_dict}")
            if task_view_choice in task_dict:
                raise Exception("Not finished 'view my task' feature")
        if user_option_select_choice == "2":
            edit_task_choice = input("Which task would you like to edit?")
            if edit_task_choice in task_dict:
                raise Exception("Not finished 'edit my task' feature")
        if user_option_select_choice == 3:
            raise Exception("Not finished 'create a task' feature")
            new_task_input_title = input("Please enter the title of your task.")
            new_task_input_description = input("Please enter the description of your task.")
            new_task_input_priority = input("Please enter the priority of your task:\nlow\nmedium\nhigh")
            new_task_input_completion_status = input("Please enter the completetion status of your task:\n1. yet to begin\n2. begun\n3. almost complete")
            new_task_input_due_date = input("Please enter the due date of your task.")
            new_task = Task()
        if user_option_select_choice == "4":
            print("Goodbye and see you soon!")
            main_loop = False
            return

    

        
    

    


if __name__ == "__main__":
    main()