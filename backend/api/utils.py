
import requests
from backend.settings import API_ENDPOINT, DISCORD_SERVER_ID,DISCORD_BOT_TOKEN


def join_server(access_token,user_id, roles):
    data ={
        "access_token": f"{access_token}",
        "roles" : roles 
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}" 
    }
    url = f"{API_ENDPOINT}/guilds/{DISCORD_SERVER_ID}/members/{user_id}"
    response = requests.put(url, json=data, headers=headers)
    return response.status_code
    
def add_role(user_id, role):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}" 
    }
    url = f"{API_ENDPOINT}/guilds/{DISCORD_SERVER_ID}/members/{user_id}/roles/{role}"
    response = requests.put(url, headers=headers)
    return response.status_code
