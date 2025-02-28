# app/view/view.py
import flet as ft
import threading

class TaskView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Flet Task Master"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.window.width = 100
        self.page.bgcolor = ft.Colors.GREY_50
        # close any open banners on app startup
        self.page.banner = None
        self.page.update()
        
        # check if accessing from desktop platform
        self.is_desktop = self.page.platform in [ft.PagePlatform.LINUX, ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS]
        self.is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
        print("User connected!")
        print("User platform:", self.page.platform)
        print("User IP:", self.page.client_ip)
        self.page.padding = ft.padding.all(25) if self.is_desktop else None

        # priority options (also defined in model for consistency)
        self.PRIORITY_OPTIONS = ["high", "med", "low"]
        self.PRIORITY_COLORS = {
            "high": ft.Colors.RED_100,
            "med": ft.Colors.AMBER_100,
            "low": ft.Colors.GREEN_ACCENT_100,
        }

        # priority selection dropdown
        self.priority_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(p) for p in self.PRIORITY_OPTIONS],
            value="low",
            label="Priority",
            expand=False,
            width=100,
        )
        # main app container (adjusts width based on screen size)
        self.main_column = ft.Column(
            [],
            width=600 if self.is_desktop else None,
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # input field for users to type in their task
        self.task_input = ft.TextField(label="Enter a task", expand=True)

        # column to hold all tasks
        self.task_list = ft.Column(scroll=ft.ScrollMode.AUTO) # makes the task list scrollable

        # defining the banner
        self.task_already_exists_warning = ft.Banner(
            bgcolor=ft.Colors.RED_400,
            leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=15),
            content=ft.Text("Task already exists!", color=ft.Colors.WHITE),  # Content will be updated dynamically
            actions=[
                ft.TextButton(text="Close",
                            # on_click=lambda e: close_banner(task_already_exists_warning),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE))
            ],
        )

        self.empty_task_warning = ft.Banner(
            bgcolor=ft.Colors.RED_400,
            leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.WHITE, size=15),
            content=ft.Text("Task cannot be empty!", color=ft.Colors.WHITE),  # Content will be updated dynamically
            actions=[
                ft.TextButton(text="Close",
                            # on_click=lambda e: close_banner(empty_task_warning),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE))
            ],
        )

        self.error_warning = ft.Banner(
            bgcolor=ft.Colors.RED_400,
            leading=ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=15),
            content=ft.Text("An error occurred. Please try again later.", color=ft.Colors.WHITE),  
            actions=[
                ft.TextButton(text="Close",
                            # on_click=lambda e: close_banner(error_warning),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE))
            ],
        )

        # button that triggers add_task function when clicked
        self.add_button = ft.ElevatedButton("Add Task") if self.is_desktop else ft.IconButton(icon=ft.Icons.ADD_CIRCLE_ROUNDED, icon_size=55)

    def show_banner(self, banner):
        self.page.banner = banner
        self.page.open(banner) # open the banner
        self.page.update()

        # Automatically close banner after 2 seconds
        threading.Timer(2, lambda: self.close_banner(banner)).start()

    def close_banner(self, banner):
        self.page.close(banner)
        self.page.update()

    def create_task_row(self, task_id, task_text, task_is_completed, task_priority, callbacks):
        # convert priority integer to readable text
        priority_text = task_priority  # Already passed as text from presenter

        # create priority label
        priority_label = ft.Container(
            content=ft.Text(priority_text, size=12, weight=ft.FontWeight.BOLD),
            bgcolor=self.PRIORITY_COLORS.get(priority_text, ft.Colors.GREY),
            padding=ft.padding.all(5),
            border_radius=5,
            visible=True
        )

        priority_edit_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(p) for p in self.PRIORITY_OPTIONS],
            value=task_priority,
            width=70,
            label=str(task_priority),
            visible=False # hidden by default
        )

        # task label (default view mode)
        task_label = ft.Text(
            task_text,
            no_wrap=False,
            expand=True,
            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if task_is_completed else ft.TextDecoration.NONE),
            color=ft.Colors.GREY_400 if task_is_completed else ft.Colors.BLACK
        )

        # edit text field (hidden by default)
        text_field = ft.TextField(
            value=task_text,
            expand=True,
            visible=False,
            autofocus=True,
            adaptive=True
        )

        task_checkbox = ft.Checkbox(
            value=bool(task_is_completed),
            data=task_id,
            visible=True
        )

        # edit button
        edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
        )

        # save button
        save_button = ft.IconButton(
            icon=ft.Icons.CHECK,
            visible=False # initially hidden
        )

        # cancel button
        cancel_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            visible=False # initially hidden
        )

        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
        )

        # Function to handle hover events
        def on_hover(e):
            if e.data == "true":  # Mouse entered
                task_row.bgcolor = ft.Colors.GREY_200  # Change to a subtle highlight
            else:  # Mouse left
                task_row.bgcolor = None  # Reset to default
            task_row.update()

        task_row = ft.Container(
            ft.Row(
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
            ),
            padding=ft.padding.all(5),  # Add padding around row for better spacing
            border_radius=ft.border_radius.all(5),  # Rounded corners
            on_hover=on_hover
        )

        # Bind callbacks
        task_checkbox.on_change = lambda e: callbacks["toggle_task"](e, task_label, task_id)
        edit_button.on_click = lambda e: callbacks["edit_task"](task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown)
        save_button.on_click = lambda e: callbacks["save_task"](task_id, text_field.value, priority_edit_dropdown.value, task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown)
        cancel_button.on_click = lambda e: callbacks["cancel_edit"](task_checkbox, task_label, text_field, edit_button, save_button, cancel_button, delete_button, priority_label, priority_edit_dropdown)
        delete_button.on_click = lambda e: callbacks["delete_task"](task_id, task_row)

        return task_row

    def build(self):
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
            content=self.task_list,
            expand=True
        )

        # layout
        self.main_column.controls.extend([
            header,
            task_list_container, # expand task list to fill space
            ft.Row([self.priority_dropdown, self.task_input, self.add_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) # input field and add task button aligned at bottom of screen
        ])
        self.page.add(self.main_column)

    def clear_tasks(self):
        self.task_list.controls.clear()

    def add_task_to_list(self, task_row):
        self.task_list.controls.append(task_row)

    def remove_task_from_list(self, task_row):
        self.task_list.controls.remove(task_row)

    def update(self):
        self.page.update()

    def clear_input(self):
        self.task_input.value = ""