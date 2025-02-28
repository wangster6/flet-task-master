# main.py
import flet as ft
from app.presenter.presenter import TaskPresenter

def main(page: ft.Page):
    presenter = TaskPresenter(page)
    presenter.run()

ft.app(target=main)