from rest_framework.generics import CreateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import JSONParser 

from django.http.response import JsonResponse
from django.shortcuts import redirect
import requests

from datetime import datetime
from django.urls import reverse

from .models import Contributor, Participant, Team
from .serializers import ContributorSerializer, ParticipantSerializer,TeamSerializer
from urllib.parse import urlencode
from .utils import join_server,add_role

from backend.settings import DISCORD_CLIENT_ID,DISCORD_CLIENT_SECRET,API_ENDPOINT

MAX_MEMBER = 3

@api_view(['GET'])
def get_all_contributors(request):
    if request.method == 'GET':
        contributors = Contributor.objects.all()
        
        contributors_serializer = ContributorSerializer(contributors, many=True)
        return JsonResponse(contributors_serializer.data, safe=False)


@api_view(['GET'])
def timeleft(request):
    if request.method == 'GET':        
        dayJ= EVENT_DATE
        now = datetime.now()

        
        if dayJ < now :#after event
            delta = now - now
        else:
            delta = dayJ - now

        secs = delta.seconds
        timedata=dict()
        timedata["days"] = delta.days
        timedata["hours"] = secs // 3600
        timedata["minutes"] = (secs // 60) % 60
        timedata["seconds"] = secs % 60 

        return JsonResponse(timedata, safe=False)

class ParticipantCreateAPIView(CreateAPIView):

    renderer_classes = [JSONRenderer]
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    
    def create(self, request, *args, **kwargs):
        # getting serializer
        serializer = self.get_serializer(data=request.data)
        # validating data 
        serializer.is_valid(raise_exception=True)

        # save particpant
        participant = self.perform_create(serializer)

        # get url of confirmation
        redirect_url =  request.build_absolute_uri(reverse('api:registration_confirmation'))
        oauth_url = get_oauth2(redirect_url,str(participant.id))
        # send confirmation to the email of participant
        sendConfirmation(participant.email,participant.fullname,oauth_url)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        if (self.request.data.get('study_at') == 'other'):
            participant=  serializer.save(study_at=self.request.data.get('other_name'))
            return participant
        participant= serializer.save()
        return participant


def get_oauth2(redirect_url,participant_id):
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_url,
        "response_type" : "code",
        "scope": "identify guilds.join",
        "state":participant_id
    }
    oauth_url =  API_ENDPOINT + '/oauth2/authorize?'  + urlencode(data)
    return oauth_url




@api_view(['GET'])
def confirm_participant(request):
    """
        confirm a participant : 
            Receive a code and participant id in the get query 
    """
    if request.method == 'GET':
        code = request.GET.get('code',None)
        if not code:
            return redirect('main:registrations')
        state = request.GET.get('state',None)
        if not state:
            return redirect('main:registrations')
        try:
            particpant = Participant.objects.get(id=state)
        except ObjectDoesNotExist:
            return redirect('main:registrations')
        
        ## here we are sure that we have identified  participant and get a code 
        redirect_url =  request.build_absolute_uri(reverse('api:registration_confirmation'))
        data = {
          "client_id": DISCORD_CLIENT_ID,
          "client_secret": DISCORD_CLIENT_SECRET,
          'grant_type': 'authorization_code',
          'code': code,
          'redirect_uri': redirect_url
        }
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
        r.raise_for_status()
        response = r.json()
        access_token = response["access_token"]
        # After we got the access_token now we can  do whatever we need 

        ## get the current user data 
        response = requests.get(f'{API_ENDPOINT}/users/@me', headers={
            "Authorization":f"Bearer {access_token}"
        })
        # here we got our user ! 
        user = response.json()

        # here check that the discord id has still not been added 
        participants = Participant.objects.filter(discord_id=user["id"])
        if participants.count()>0:
            return JsonResponse({"error":"You are already registered and you have joined the server space. thank you for checking our discord server"},safe=False)


        # save our participant
        particpant.discord_id = user["id"]
        particpant.discord_username = user["username"]
        particpant.save()
        status = join_server(access_token,user['id'],[842454863446016021])
        if status ==204:
            # user already in the server 
            add_role(user['id'],842454863446016021)
        return redirect("https://www.gdgalgiers.com/discord")
    
    return JsonResponse({},safe=False)

##################################################
#           Hack The Bot Commands 
#
###################################################


@api_view(['GET'])
def GetParticipant(request,participant_id=None):
    try :
        participant = Participant.objects.get(pk=participant_id)
        participant_serializer = ParticipantSerializer(participant)
        team_serializer = TeamSerializer(participant.team)
        data=participant_serializer.data
        data["team"]=team_serializer.data
        return JsonResponse(data,safe=False)
    except Participant.DoesNotExist:
        return JsonResponse({"status":"Participant not found"},safe=False)
    # except :
    #     return JsonResponse({"status":"NO_PARTICIPANT"},safe=False)
        

@api_view(['POST'])
def verify(request):
    data = JSONParser().parse(request)
    if 'discord_id' not in data:
        return JsonResponse({"status":"NO_PARTICIPANT"},safe=False)
    discord_id = data["discord_id"]
    participants = Participant.objects.filter(discord_id=discord_id)
    if len(participants) == 0:
        return JsonResponse({"status":"UNAUTHORIZED"},safe=False)
    elif len(participants) > 1:
        return JsonResponse({"status":"UNKNOWN_ERROR"},safe=False)
    participant_serializer = ParticipantSerializer(participants[0])
    return JsonResponse({
        "status":"SUCCESS",
        "participant_id" : participant_serializer.data['id']
        },safe=False)


@api_view(['POST'])
def CreateTeam(request,participant_id=None):
    if request.method == "POST":
        try:
            participant = Participant.objects.get(pk=participant_id)
            if participant.team != None:
                return JsonResponse({"status":"ALREADY_IN_A_TEAM"},safe=False)
            team_data = JSONParser().parse(request)
            teams = Team.objects.filter(name=team_data["name"])
            if teams.count()> 0:
                return JsonResponse({"status":"TEAM_ALREADY_EXIST"},safe=False)
            
            team, created = Team.objects.get_or_create(**team_data)
        except Participant.DoesNotExist:
            return JsonResponse({"status":"Participant not found"},safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({"status":"UNKNOWN_ERROR"},safe=False)

        if not created : 
            return JsonResponse({"status":"TEAM_ALREADY_EXIST"},safe=False)
        else:
            
            participant.is_leader = True
            participant.team =team

            participant_serializer = ParticipantSerializer(participant,data=participant.__dict__)

            if participant_serializer.is_valid():
                participant_serializer.save()
            return JsonResponse({"status":"SUCCESS","token":team.token},safe=False)


@api_view(['POST'])
def JoinTeam(request,participant_id=None):
    if request.method == "POST":
        try:
            participant = Participant.objects.get(pk=participant_id)
            if participant.team !=None :
                return JsonResponse({"status":"you're already in a team"},safe=False)
                
            token = JSONParser().parse(request)['token']
            team = Team.objects.get(token=token)

            nb_members = Participant.objects.filter(team=team)
            if len(nb_members) > MAX_MEMBER:
                return JsonResponse({"status":f"max number of members is {MAX_MEMBER}"},safe=False)
            
            elif len(nb_members) == 0:
                return JsonResponse({"status":f"Incorrect token"},safe=False)

            participant.team = team
            participant_serializer = ParticipantSerializer(participant, data=participant.__dict__)
            if participant_serializer.is_valid():
                participant_serializer.save()

            return JsonResponse({
                "status":"SUCCESS",
                "team_name": team.name,
                "message": f"You have successfully joined {team.name}"
                })
        except Participant.DoesNotExist:
            return JsonResponse({"status":"Participant not found"},safe=False)
        except:
            return JsonResponse({"status":"UNKNOWN_ERROR"},safe=False)


@api_view(['DELETE'])
def RemoveMemberFromTeam(request,participant_id=None):
    if request.method == "DELETE":
        try:
            participant = Participant.objects.get(pk=participant_id)
            if participant.is_leader:
                memberToRemove = JSONParser().parse(request)['member']
                if memberToRemove == participant_id:
                    return JsonResponse({"status":"you cannot delete yourself"},safe=False)

                members = Participant.objects.filter(team=participant.team).filter(id=memberToRemove)
                if len(members) == 1:
                    member = members[0]
                    print(member)
                    member.team = None
                    member_serializer = ParticipantSerializer(member, data=member.__dict__)
                    if member_serializer.is_valid():
                        member_serializer.save()
                    return JsonResponse({"status":"SUCCESS"})
                else:
                    return JsonResponse({"status":"Wrong partcipant_id"},safe=False)
            else:
                return JsonResponse({"status":"You're not allowed to do that"},safe=False)
        except Participant.DoesNotExist:
            return JsonResponse({"status":"Participant not found"},safe=False)
        except:
            return JsonResponse({"status":"UNKNOWN_ERROR"},safe=False)