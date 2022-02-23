
import requests
from backend.settings import API_ENDPOINT, DISCORD_SERVER_ID,DISCORD_BOT_TOKEN
from .models import  Participant
import csv

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
def FromcsvtoDB():
    file = open('participants.csv',encoding="utf-8-sig")
    content = csv.reader(file,delimiter=',')
    line=0
    for row in content:
        if line == 0:
            columns=row[0].split(";")
            line += 1
        else:
            data=row[0].split(";")
            user={}
            for i in range(len(data)):
                print(columns[i])
                user[columns[i]]=data[i]
    Participant.objects.create(**user)

FromcsvtoDB()