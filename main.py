import flet as ft
import threading
from supabase import create_client, Client

# # IMPORTS FOR OFFICIAL DEPLOYMENT
# import boto3
# import json

# IMPORTS FOR TESTING
import os
from dotenv import load_dotenv

# # GET SUPABASE SECRETS FROM AWS SSM. USED IN OFFICIAL DEPLOYMENT
# def get_ssm_parameter(name, with_decryption=True):
#     """Retrieve a parameter from AWS SSM Parameter Store."""
#     ssm = boto3.client('ssm', region_name="us-east-1")  # Change to your region
#     response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
#     return response['Parameter']['Value']

# # fetch secrets from AWS SSM Parameter Store
# SUPABASE_URL = get_ssm_parameter("/flettaskmaster/supabase-url", with_decryption=True)
# SUPABASE_KEY = get_ssm_parameter("/flettaskmaster/supabase-key", with_decryption=True)

# # GET SUPABASE SECRETS FROM ENV FILE. USED IN TESTING
# load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# initialize supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Flet Task Master"
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.padding = ft.padding.all(25)

    # close any open banners on app startup
    page.banner = None
    page.update()
    
    # input field for users to type in their task
    task_input = ft.TextField(label="Enter a task", expand=True)

    # column to hold all tasks
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO) # makes the task list scrollable

    # defining the banner
    task_already_exists_warning = ft.Banner(
        bgcolor=ft.Colors.RED_400,
        leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=15),
        content=ft.Text("Task already exists!", color=ft.Colors.WHITE),  # Content will be updated dynamically
        actions=[
            ft.TextButton(text="Close",
                          on_click=lambda e: close_banner(task_already_exists_warning),
                          style=ft.ButtonStyle(color=ft.Colors.WHITE))
        ],
    )

    empty_task_warning = ft.Banner(
        bgcolor=ft.Colors.RED_400,
        leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=15),
        content=ft.Text("Cannot add an empty task!", color=ft.Colors.WHITE),  # Content will be updated dynamically
        actions=[
            ft.TextButton(text="Close",
                          on_click=lambda e: close_banner(empty_task_warning),
                          style=ft.ButtonStyle(color=ft.Colors.WHITE))
        ],
    )

    error_warning = ft.Banner(
        bgcolor=ft.Colors.RED_400,
        leading=ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=15),
        content=ft.Text("An error occurred. Please try again later.", color=ft.Colors.WHITE),  
        actions=[
            ft.TextButton(text="Close",
                        on_click=lambda e: close_banner(error_warning),
                        style=ft.ButtonStyle(color=ft.Colors.WHITE))
        ],
    )

    def show_banner(banner):
        page.banner = banner
        page.open(banner) # open the banner
        page.update()

        # Automatically close banner after 2 seconds
        threading.Timer(2, lambda: close_banner(banner)).start()

    def close_banner(banner):
        page.close(banner)
        page.update()

    def create_task_row(task_id, task_text, task_is_completed):
        # task label (default view mode)
        task_label = ft.Text(task_text, no_wrap=False, expand=True)

        # edit text field (hidden by default)
        text_field = ft.TextField(value=task_text, expand=True, visible=False)

        # function to update task text in database
        def update_task(e):
            new_text = text_field.value.strip()
            if not new_text:
                show_banner(empty_task_warning)
                return
            
            try:
                supabase.table("tasks").update({"text": new_text}).eq("id", task_id).execute()
                task_label.value = new_text
                task_label.visible = True
                text_field.visible = False # hide input after updating
                save_button.visible = False
                cancel_button.visible = False
                edit_button.visible = True
                delete_button.visible = True
                page.update()
            except Exception as ex:
                print("Error updating task")
                show_banner(error_warning)

        def on_edit_click(e):
            edit_task(e)
            save_button.visible = True
            cancel_button.visible = True
            edit_button.visible = False
            delete_button.visible = False
            page.update()

        # function to toggle between viewing and editing mode
        def edit_task(e):
            task_label.visible = False # hide task label
            text_field.visible = True # show input field
            text_field.value = task_label.value
            text_field.focus()
            page.update()

        # function to cancel editing
        def cancel_edit(e):
            task_label.visible = True # show task label
            text_field.visible = False # hide input field
            save_button.visible = False
            cancel_button.visible = False
            edit_button.visible = True
            delete_button.visible = True
            page.update()
        
        # save button
        save_button = ft.IconButton(
            icon=ft.Icons.CHECK,
            on_click=update_task,
            visible=False # initially hidden
        )

        # cancel button
        cancel_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=cancel_edit,
            visible=False # initially hidden
        )

        # edit button
        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            on_click=on_edit_click
        )

        def delete_task(e, task_id, task_row):
            try:
                supabase.table("tasks").delete().eq("id", task_id).execute()
                task_list.controls.remove(task_row)
                page.update()
            except Exception as ex:
                print("Error deleting task")
                show_banner(error_warning)
        
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            on_click=lambda e: delete_task(e, task_id, task_row)
        )

        task_checkbox = ft.Checkbox(
            on_change=lambda e, task_label=task_label, task_id=task_id: toggle_task(e, task_label, task_id),
            value=bool(task_is_completed),
            data=task_id
        )

        task_row = ft.Row(
            [
                task_checkbox,
                task_label,
                text_field,
                edit_button,
                save_button,
                cancel_button,
                delete_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )

        return task_row

    # function to handle checkbox changes
    def toggle_task(e, task_label, task_id):
        checkbox = e.control # get checkbox that triggered the event
        is_completed = checkbox.value

        try:
            supabase.table("tasks").update({"completed": is_completed}).eq("id", task_id).execute()
            task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if is_completed else ft.TextStyle(decoration=ft.TextDecoration.NONE)
            task_label.update() # refresh the checkbox UI
        except Exception as ex:
            print("Erorr updating task status")
            show_banner(error_warning)

    def load_tasks():
        task_list.controls.clear()
        try:
            response = supabase.table("tasks").select("*").execute()
            for task in response.data:
                task_id = task["id"]
                task_text = task["text"]
                task_is_completed = task["completed"]
                task_list.controls.append(create_task_row(task_id, task_text, task_is_completed))
            page.update()
        except Exception as ex:
            print("Error loading tasks",)
            show_banner(error_warning)

    # function to add a task when button is clicked
    def add_task(e):
        task_text = task_input.value.strip() # get input text
        if not task_text:
            show_banner(empty_task_warning)
            return  # exit function if input is empty

        try:
            response = supabase.table("tasks").insert({"text": task_text, "completed": False}).execute()
            task_id = response.data[0]["id"]

            task_list.controls.append(create_task_row(task_id, task_text, False))
            task_input.value = ""  # clear input field
            page.update()  # refresh UI
        except Exception as ex:
            if "duplicate key value" in str(ex):  # catch unique constraint error
                show_banner(task_already_exists_warning)
            else:
                print("Error adding task")
                show_banner(error_warning)
    
    ## APP MAIN FUNCTIONALITY IS STARTED
    load_tasks() # load tasks on app startup

    # button that triggers add_task function when clicked
    add_button = ft.ElevatedButton("Add Task", on_click=add_task)
    
    ## CONTAINERS
    # header centered at top of screen
    header = ft.Container(
        content=ft.Row(
            [ft.Text("To Do", size=24, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER, # aligns header to center of screen
        ),
        padding=ft.padding.only(bottom=25) # added padding below header
    )

    # wrap task list in fixed height container to prevent overflow
    task_list_container = ft.Container(
        content=task_list,
        height=400,
        expand=True
    )

    # layout
    page.add(
        header,
        task_list_container, # expand task list to fill space
        ft.Row([task_input, add_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) # input field and add task button aligned at bottom of screen
    )

ft.app(target=main)