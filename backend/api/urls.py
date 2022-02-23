# from django.conf.urls import url 
from django.urls import path,re_path
from api import views


urlpatterns = [
    path('participants/register',views.RegisterParticipant),
    re_path('participants/',views.get_all_participants),
    re_path('organizers/',views.get_all_organizers),
    re_path('mentors/',views.get_all_mentors),
    #re_path('contributors/', views.get_all_contributors),
    #re_path('timeleft', views.timeleft),
    #path('participant/register', views.ParticipantCreateAPIView.as_view(),name="participants_registration"),
    path('participant/verify', views.verify,name="participant_verify"),
    path('participant/<uuid:participant_id>',views.GetParticipant,name="get_participant"),
    path('participant/<uuid:participant_id>/team/create',views.CreateTeam,name="create_team"),
    path('participant/<uuid:participant_id>/team/join',views.JoinTeam,name="join_team")
]