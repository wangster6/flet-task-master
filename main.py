import flet as ft
import os
import threading
from supabase import create_client, Client
from dotenv import load_dotenv

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
        leading=ft.Icon(ft.Icons.WARNING, color=ft.colors.WHITE, size=15),
        content=ft.Text("Task already exists!", color=ft.colors.WHITE),  # Content will be updated dynamically
        actions=[
            ft.TextButton(text="Close",
                          on_click=lambda e: close_banner(task_already_exists_warning),
                          style=ft.ButtonStyle(color=ft.colors.WHITE))
        ],
    )

    empty_task_warning = ft.Banner(
        bgcolor=ft.Colors.RED_400,
        leading=ft.Icon(ft.Icons.WARNING, color=ft.colors.WHITE, size=15),
        content=ft.Text("Cannot add an empty task!", color=ft.colors.WHITE),  # Content will be updated dynamically
        actions=[
            ft.TextButton(text="Close",
                          on_click=lambda e: close_banner(empty_task_warning),
                          style=ft.ButtonStyle(color=ft.colors.WHITE))
        ],
    )

    error_warning = ft.Banner(
        bgcolor=ft.Colors.RED_400,
        leading=ft.Icon(ft.Icons.ERROR, color=ft.colors.WHITE, size=15),
        content=ft.Text("An error occurred. Please try again later.", color=ft.colors.WHITE),  
        actions=[
            ft.TextButton(text="Close",
                        on_click=lambda e: close_banner(error_warning),
                        style=ft.ButtonStyle(color=ft.colors.WHITE))
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

    # function to handle checkbox changes
    def toggle_task(e, task_label, task_id):
        checkbox = e.control # get checkbox that triggered the event
        is_completed = checkbox.value

        try:
            supabase.table("tasks").update({"completed": is_completed}).eq("id", task_id).execute()
            task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if is_completed else ft.TextStyle(decoration=ft.TextDecoration.NONE)
            task_label.update() # refresh the checkbox UI
        except Exception as ex:
            print("Erorr updating task status:", ex)
            show_banner(error_warning)

    def load_tasks():
        task_list.controls.clear()
        try:
            response = supabase.table("tasks").select("*").execute()

            for task in response.data:
                task_id = task["id"]
                task_text = task["text"]
                task_is_completed = task["completed"]

                def delete_task(e, task_id, task_row):
                    try:
                        supabase.table("tasks").delete().eq("id", task_id).execute()
                        task_list.controls.remove(task_row)
                        page.update()
                    except Exception as ex:
                        print("Error deleting task:", ex)
                        show_banner(error_warning)
                    
                task_label = ft.Text(task_text, no_wrap=False, expand=True)
                task_checkbox = ft.Checkbox(
                    on_change=lambda e, task_label=task_label, task_id=task_id: toggle_task(e, task_label, task_id),
                    value=bool(task_is_completed),
                    data=task_id
                )

                task_row = ft.Row(
                    [
                        task_checkbox,
                        task_label
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=True
                )

                delete_button = ft.IconButton(
                    icon=ft.icons.DELETE,
                    on_click=lambda e, task_id=task_id, task_row=task_row: delete_task(e, task_id, task_row)
                ) # create delete button for task

                task_row.controls.append(delete_button)

                task_list.controls.append(task_row)
            page.update()
        except Exception as ex:
            print("Error loading tasks:", ex)
            show_banner(error_warning)

    # function to add a task when button is clicked
    def add_task(e):
        task_text = task_input.value.strip() # get input text
        if not task_text:
            show_banner(empty_task_warning)
            return # exit function if input is empty
        
        # check if task already exists in Supabase
        try:
            response = supabase.table("tasks").select("id").eq("text", task_text).execute()
            if response.data:
                show_banner(task_already_exists_warning)
                return # exit function without adding duplicate task
        except Exception as ex:
            print("Error checking for existing task:", ex)
            show_banner(error_warning)
            return

        if task_text: # check if text is not empty
            response = supabase.table("tasks").insert({"text": task_text, "completed": False}).execute()
            task_id = response.data[0]["id"]

            # function to delete task when button is clicked
            def delete_task(e, task_id, task_row):
                try:
                    supabase.table("tasks").delete().eq("id", task_id).execute()
                    task_list.controls.remove(task_row)
                    page.update()
                except Exception as ex:
                    print("Error deleting task:", ex)
                    show_banner(error_warning)
                
            # wrap task label in text widget to allow wrapping
            task_label = ft.Text(task_text, no_wrap=False, expand=True)

            task_checkbox = ft.Checkbox(
                on_change=lambda e, task_label=task_label, task_id=task_id: toggle_task(e, task_label=task_label, task_id=task_id),
                data=task_id
            ) # create checkbox for task

            # organize elements into a row. align checkbox to the left and delete button to the right
            task_row = ft.Row(
                [
                    task_checkbox,
                    task_label
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True
            )

            delete_button = ft.IconButton(
                icon=ft.icons.DELETE,
                on_click=lambda e, task_id=task_id, task_row=task_row: delete_task(e, task_id, task_row)
            ) # create delete button for task

            task_row.controls.append(delete_button)

            task_list.controls.append(task_row) # add task to list
            task_input.value = "" # clear input field
            page.update() # refresh the page UI
    
    load_tasks() #load tasks on app startup

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