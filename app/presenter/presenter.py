# app/presenter/presenter.py
from app.model.model import TaskModel, PRIORITY_REVERSE_MAPPING
from app.view.view import TaskView

class TaskPresenter:
    def __init__(self, page):
        self.model = TaskModel()
        self.view = TaskView(page)
        self.setup_callbacks()

    def setup_callbacks(self):
        self.view.add_button.on_click = self.add_task
        self.view.task_already_exists_warning.actions[0].on_click = lambda e: self.view.close_banner(self.view.task_already_exists_warning)
        self.view.empty_task_warning.actions[0].on_click = lambda e: self.view.close_banner(self.view.empty_task_warning)
        self.view.error_warning.actions[0].on_click = lambda e: self.view.close_banner(self.view.error_warning)

    def load_tasks(self):
        # function to load tasks
        self.view.clear_tasks()
        try:
            tasks = self.model.load_tasks()
            for task in tasks:
                task_id = task["id"]
                task_text = task["text"]
                task_is_completed = task["completed"]
                task_priority = task["priority"]
                task_row = self.view.create_task_row(
                    task_id, task_text, task_is_completed, PRIORITY_REVERSE_MAPPING[task_priority],
                    {
                        "toggle_task": self.toggle_task,
                        "edit_task": self.on_edit_click,
                        "save_task": self.on_save_edit,
                        "cancel_edit": self.on_cancel_edit,
                        "delete_task": self.delete_task
                    }
                )
                self.view.add_task_to_list(task_row)
            self.view.update()
        except Exception as ex:
            print("Error loading tasks:", ex)
            self.view.show_banner(self.view.error_warning)

    # function to add a task when button is clicked
    def add_task(self, e):
        task_text = self.view.task_input.value.strip() # get input text
        try:
            task_data = self.model.add_task(task_text, self.view.priority_dropdown.value)
            task_id = task_data["id"]
            task_row = self.view.create_task_row(
                task_id, task_text, False, PRIORITY_REVERSE_MAPPING[task_data["priority"]],
                {
                    "toggle_task": self.toggle_task,
                    "edit_task": self.on_edit_click,
                    "save_task": self.on_save_edit,
                    "cancel_edit": self.on_cancel_edit,
                    "delete_task": self.delete_task
                }
            )
            self.view.add_task_to_list(task_row)
            # sort task list after adding task
            self.load_tasks()
            self.view.clear_input()  # clear input field
            self.view.update()  # refresh UI
        except ValueError as ve:
            if str(ve) == "Task already exists":
                self.view.show_banner(self.view.task_already_exists_warning)
            elif str(ve) == "Task cannot be empty":
                self.view.show_banner(self.view.empty_task_warning)
        except Exception as ex:
            print("Error adding task:", ex)
            self.view.show_banner(self.view.error_warning)

    # function to handle checkbox changes
    def toggle_task(self, e, task_label, task_id):
        checkbox = e.control # get checkbox that triggered the event
        is_completed = checkbox.value
        try:
            self.model.update_task(task_id, task_label.value, PRIORITY_REVERSE_MAPPING[self.model.tasks[[t["id"] for t in self.model.tasks].index(task_id)]["priority"]], is_completed)
            self.load_tasks()
        except Exception as ex:
            print("Error updating task status:", ex)
            self.view.show_banner(self.view.error_warning)

    # function to toggle between viewing and editing mode
    def on_edit_click(self, task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown):
        task_checkbox.visible = False
        task_label.visible = False # hide task label
        text_field.visible = True # show input field
        text_field.value = task_label.value
        text_field.focus()
        save_button.visible = True
        cancel_button.visible = True
        edit_button.visible = False
        delete_button.visible = False
        priority_edit_dropdown.visible = True
        priority_label.visible = False
        self.view.update()

    # function to update task text in database
    def on_save_edit(self, task_id, new_text, new_priority, task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown):
        try:
            self.model.update_task(task_id, new_text, new_priority, task_checkbox.value)
            self.load_tasks()
            # update UI
            task_checkbox.visible = True
            task_label.visible = True
            text_field.visible = False # hide input after updating
            save_button.visible = False
            cancel_button.visible = False
            edit_button.visible = True
            delete_button.visible = True
            priority_edit_dropdown.visible = False
            priority_label.visible = True
            self.view.update()
        except ValueError as ve:
            if str(ve) == "Task cannot be empty":
                self.view.show_banner(self.view.empty_task_warning)
        except Exception as ex:
            print("Error updating task:", ex)
            self.view.show_banner(self.view.error_warning)

    # function to cancel editing
    def on_cancel_edit(self, task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown):
        task_checkbox.visible = True
        task_label.visible = True # show task label
        text_field.visible = False # hide input field
        save_button.visible = False
        cancel_button.visible = False
        edit_button.visible = True
        delete_button.visible = True
        priority_edit_dropdown.visible = False
        priority_label.visible = True
        self.view.update()

    def delete_task(self, task_id, task_row):
        # Note: Original delete_task had a lambda with parameters, but here we pass them directly
        try:
            self.model.delete_task(task_id)
            self.view.remove_task_from_list(task_row)
            self.view.update()
        except Exception as ex:
            print("Error deleting task")
            self.view.show_banner(self.view.error_warning)

    def run(self):
        ## APP MAIN FUNCTIONALITY IS STARTED
        self.load_tasks() # load tasks on app startup
        self.view.build()