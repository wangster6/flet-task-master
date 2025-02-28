# app/model/model.py
import flet as ft
import threading
import bleach
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
    "low": 2
}
# PRIORITY_REVERSE_MAPPING = {v: k for k, v in PRIORITY_MAPPING.items()}
PRIORITY_REVERSE_MAPPING = {
    0: "high",
    1: "med",
    2: "low"
}

class TaskModel:
    def __init__(self):
        self.tasks = []

    def load_tasks(self):
        try:
            response = supabase.table("tasks").select("*").execute()
            # sort tasks by priority before adding to UI
            sorted_tasks = sorted(response.data, key=lambda t: (t["completed"], t["priority"]))
            self.tasks = sorted_tasks
            return self.tasks
        except Exception as ex:
            raise Exception(f"Error loading tasks: {ex}")

    def add_task(self, text, priority):
        text = self.sanitize_input(text)
        if not text:
            raise ValueError("Task cannot be empty")
        try:
            task_priority = PRIORITY_MAPPING[priority]
            response = supabase.table("tasks").insert({"text": text, "completed": False, "priority": task_priority}).execute()
            return response.data[0]
        except Exception as ex:
            if "duplicate key value" in str(ex):  # catch unique constraint error
                raise ValueError("Task already exists")
            raise Exception(f"Error adding task: {ex}")

    def update_task(self, task_id, text, priority, completed):
        text = self.sanitize_input(text)
        if not text:
            raise ValueError("Task cannot be empty")
        try:
            new_priority = PRIORITY_MAPPING[priority]
            supabase.table("tasks").update({"text": text, "priority": new_priority, "completed": completed}).eq("id", task_id).execute()
        except Exception as ex:
            raise Exception(f"Error updating task: {ex}")

    def delete_task(self, task_id):
        try:
            supabase.table("tasks").delete().eq("id", task_id).execute()
        except Exception as ex:
            raise Exception(f"Error deleting task: {ex}")

    # sanitize user input using bleach to protect against attacks
    def sanitize_input(self, user_input):
        return bleach.clean(user_input)