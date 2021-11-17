from rest_framework import serializers 
from api.models import Contributor, Participant, Team

# class ContributorSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Contributor
#         fields = (
#             'id',
#             'name',
#             'type',
#             'description',
#             'picture',
#             'facebook_url',
#             'instagram_url',
#             'linkedin_url',
#             'twitter_url',
#         )

# class ParticipantSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Participant
#         fields = '__all__'

# class TeamSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Team
#         fields = (
#             'id',
#             'name',
#             'token',
#             'image'
#         )
        