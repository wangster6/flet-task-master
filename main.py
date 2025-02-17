import flet as ft

def main(page: ft.Page):
    page.title = "Flet Task Master"
    page.vertical_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
    page.padding = ft.padding.all(25)
    
    # input field for users to type in their task
    task_input = ft.TextField(label="Enter a task", expand=True)

    # column to hold all tasks
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO) # makes the task list scrollable

    # function to handle checkbox changes
    def toggle_task(e):
        checkbox = e.control # get checkbox that triggered the event

        if checkbox.value: # if checkbox is checked
            checkbox.label_style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
        else:
            checkbox.label_style = ft.TextStyle(decoration=ft.TextDecoration.NONE)

        checkbox.update() # refresh the checkbox UI

    # function to add a task when button is clicked
    def add_task(e):
        task_text = task_input.value # get input text
        if task_text.strip(): # check if text is not empty
            # function to delete task when button is clicked
            def delete_task(e):
                task_list.controls.remove(task_row)
                page.update()

            task_checkbox = ft.Checkbox(on_change=toggle_task) # create checkbox for task
            delete_button = ft.IconButton(icon=ft.icons.DELETE, on_click=delete_task) # create delete button for task

            # wrap task label in text widget to allow wrapping
            task_label = ft.Text(task_text, no_wrap=False, expand=True)
            task_content = ft.Row([task_checkbox, task_label], expand=True)

            # organize elements into a row. align checkbox to the left and delete button to the right
            task_row = ft.Row(
                [
                    task_content,
                    delete_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True
            )

            task_list.controls.append(task_row) # add task to list
            task_input.value = "" # clear input field
            page.update() # refresh the page UI
    
    # button that triggers add_task function when clicked
    add_button = ft.ElevatedButton("Add Task", on_click=add_task)
    
    ## CONTAINERS
    # header centered at top of screen
    header = ft.Container(
        content=ft.Row(
            [ft.Text("Task Master", size=24, weight=ft.FontWeight.BOLD)],
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