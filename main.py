import flet as ft

def main(page: ft.Page):
    page.title = "Flet Task Master"
    
    # input field for users to type in their task
    task_input = ft.TextField(label="Enter a task", expand=True)

    # column to hold all tasks
    task_list = ft.Column()

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
            task_checkbox = ft.Checkbox(label=task_text, on_change=toggle_task) # create checkbox for task
            task_list.controls.append(task_checkbox) # add task to list
            task_input.value = "" # clear input field
            page.update() # refresh the page UI
    
    # button that triggers add_task function when clicked
    add_button = ft.ElevatedButton("Add Task", on_click=add_task)
    
    # layout
    page.add(
        ft.Row([task_input, add_button]),
        task_list
    )

ft.app(target=main)