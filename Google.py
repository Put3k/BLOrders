import pickle
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime

from utils import resource_path


def create_service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep="-")
    scopes = [scope for scope in scopes[0]]

    cred = None

    pickle_file = f"token_{api_name}_{api_version}.pickle"

    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            cred = flow.run_local_server()

        with open(pickle_file, "wb") as token:
            pickle.dump(cred, token)

    try:
        service = build(api_name, api_version, credentials=cred, static_discovery=False)
        print(api_name, "service created successfully")
        return service
    except Exception as e:
        raise Exception(e)


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + "Z"
    return dt


def get_credentials():
    if getattr(sys, "frozen", False):
        return resource_path("credentials.json")
    else:
        return "credentials.json"
