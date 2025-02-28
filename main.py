import flet as ft
import threading
import time
from supabase import create_client, Client

# ==================================================================== #
# FOR DEPLOYMENT

# IMPORTS
import boto3
import json

# GET SUPABASE SECRETS FROM AWS SSM. USED IN OFFICIAL DEPLOYMENT
def get_ssm_parameter(name, with_decryption=True):
    """Retrieve a parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name="us-east-1")  # Change to your region
    response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
    return response['Parameter']['Value']

# FETCH SECRETS FROM AWS SSM PARAMETER STORE
SUPABASE_URL = get_ssm_parameter("/flettaskmaster/supabase-url", with_decryption=True)
SUPABASE_KEY = get_ssm_parameter("/flettaskmaster/supabase-key", with_decryption=True)
# ==================================================================== #
# FOR TESTING

# # IMPORTS FOR TESTING
# import os
# from dotenv import load_dotenv

# # LOAD ENVIRONMENT VARIABLES
# load_dotenv()

# # GET SUPABASE SECRETS FROM ENV FILE
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# ==================================================================== #

# initialize supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Flet Task Master"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 100

    # close any open banners on app startup
    page.banner = None
    page.update()
    
    # check if accessing from desktop platform
    is_desktop = page.platform in [ft.PagePlatform.LINUX, ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS]
    is_mobile = page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
    print("User connected!")
    print("User platform:", page.platform)
    print("User IP:", page.client_ip)
    page.padding = ft.padding.all(25) if is_desktop else None

    # priority options
    PRIORITY_OPTIONS = ["high", "med", "low"]
    PRIORITY_COLORS = {
        "high": ft.Colors.RED_100,
        "med": ft.Colors.AMBER_100,
        "low": ft.Colors.GREEN_ACCENT_100,
    }
    PRIORITY_MAPPING = {
        "high": 0,
        "med": 1,
        "low": 2,
    }
    # PRIORITY_REVERSE_MAPPING = {v: k for k, v in PRIORITY_MAPPING.items()}
    PRIORITY_REVERSE_MAPPING = {0: "high", 1: "med", 2: "low"}

    # priority selection dropdown
    priority_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(p) for p in PRIORITY_OPTIONS],
        value="low",
        label="Priority",
        expand=False,
        width=100,
    )
    # main app container (adjusts width based on screen size)
    main_column = ft.Column(
        [],
        width=800 if is_desktop else None,
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

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

    def create_task_row(task_id, task_text, task_is_completed, task_priority):
        # convert priority integer to readable text
        priority_text = PRIORITY_REVERSE_MAPPING.get(task_priority, "low")

        # create priority label
        priority_label = ft.Container(
            content=ft.Text(priority_text, size=12, weight=ft.FontWeight.BOLD),
            bgcolor=PRIORITY_COLORS.get(priority_text, ft.Colors.GREY),
            padding=ft.padding.all(5),
            border_radius=5,
            visible=True
        )

        priority_edit_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(p) for p in PRIORITY_OPTIONS],
            value=task_priority,
            width=70,
            label=str(PRIORITY_REVERSE_MAPPING[task_priority]),
            visible=False # hidden by default
        )

        # task label (default view mode)
        task_label = ft.Text(task_text, no_wrap=False, expand=True)

        # edit text field (hidden by default)
        text_field = ft.TextField(
            value=task_text,
            expand=True,
            visible=False,
            autofocus=True,
            adaptive=True
        )

        # function to update task text in database
        def on_save_edit(e):
            new_text = text_field.value.strip()
            new_priority = PRIORITY_MAPPING[priority_edit_dropdown.value]
            if not new_text:
                show_banner(empty_task_warning)
                return
            
            try:
                supabase.table("tasks").update({"text": new_text, "priority": new_priority}).eq("id", task_id).execute()
                task_label.value = new_text

                # update priority
                priority_text = PRIORITY_REVERSE_MAPPING[new_priority]
                priority_label.content = ft.Text(priority_text, size=12, weight=ft.FontWeight.BOLD)
                priority_label.bgcolor = PRIORITY_COLORS.get(priority_text, ft.Colors.GREY)
                load_tasks()

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
                page.update()
            except Exception as ex:
                print("Error updating task:", ex)
                show_banner(error_warning)

        # function to toggle between viewing and editing mode
        def on_edit_click(e):
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
            page.update()

        # function to cancel editing
        def on_cancel_edit(e):
            task_checkbox.visible = True
            task_label.visible = True # show task label
            text_field.visible = False # hide input field
            save_button.visible = False
            cancel_button.visible = False
            edit_button.visible = True
            delete_button.visible = True
            priority_edit_dropdown.visible = False
            priority_label.visible = True
            page.update()
        
        # save button
        save_button = ft.IconButton(
            icon=ft.Icons.CHECK,
            on_click=on_save_edit,
            visible=False # initially hidden
        )

        # cancel button
        cancel_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=on_cancel_edit,
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
            data=task_id,
            visible=True
        )

        task_row = ft.Row(
            [
                task_checkbox,
                priority_label,
                priority_edit_dropdown,
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
            
            # sort tasks by priority before adding to UI
            sorted_tasks = sorted(response.data, key=lambda t: t["priority"])
            
            for task in sorted_tasks:
                task_id = task["id"]
                task_text = task["text"]
                task_is_completed = task["completed"]
                task_priority = task["priority"]
                task_list.controls.append(create_task_row(task_id, task_text, task_is_completed, task_priority))
            page.update()
        except Exception as ex:
            print("Error loading tasks:", ex)
            show_banner(error_warning)

    # function to add a task when button is clicked
    def add_task(e):
        task_text = task_input.value.strip() # get input text
        if not task_text:
            show_banner(empty_task_warning)
            return  # exit function if input is empty

        try:
            task_priority = PRIORITY_MAPPING[priority_dropdown.value]
            response = supabase.table("tasks").insert({"text": task_text, "completed": False, "priority": task_priority}).execute()
            task_id = response.data[0]["id"]

            task_list.controls.append(create_task_row(task_id, task_text, False, task_priority))
            # sort task list after adding task
            load_tasks()
            task_input.value = ""  # clear input field
            page.update()  # refresh UI
        except Exception as ex:
            if "duplicate key value" in str(ex):  # catch unique constraint error
                show_banner(task_already_exists_warning)
            else:
                print("Error adding task:", ex)
                show_banner(error_warning)
    
    def main_functionality():
        ## APP MAIN FUNCTIONALITY IS STARTED
        load_tasks() # load tasks on app startup

        # button that triggers add_task function when clicked
        add_button = ft.ElevatedButton("Add Task", on_click=add_task) if is_desktop else ft.IconButton(icon=ft.Icons.ADD_CIRCLE_ROUNDED, icon_size=55, on_click=add_task)
        
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
            expand=True
        )

        # layout
        main_column.controls.extend([
            header,
            task_list_container, # expand task list to fill space
            ft.Row([priority_dropdown, task_input, add_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) # input field and add task button aligned at bottom of screen
        ])
        
        page.add(main_column)
    
    main_functionality()

ft.app(target=main)
