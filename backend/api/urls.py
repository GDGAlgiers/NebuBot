from django.conf.urls import url 
from django.urls import path
from api import views 
 
urlpatterns = [ 
    url('contributors/', views.get_all_contributors),
    url('timeleft', views.timeleft),
    path('participant/register', views.ParticipantCreateAPIView.as_view(),name="participants_registration"),
    path("participant_confirm", views.confirm_participant,name="registration_confirmation"),
    path('participant/verify', views.verify,name="participant_verify"),
    path('participant/<uuid:participant_id>',views.GetParticipant,name="get_participant"),
    path('participant/<uuid:participant_id>/team/create',views.CreateTeam,name="create_team"),
    path('participant/<uuid:participant_id>/team/join',views.JoinTeam,name="join_team"),
    path('participant/<uuid:participant_id>/team/remove',views.RemoveMemberFromTeam,name="remove_member_from_team")
]