from django.contrib import admin

from rooms.models import Candidate, Membership, Room, Vote

admin.site.register(Room)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Membership)
