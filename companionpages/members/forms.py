from django.db import models
from django.forms import ModelForm

from .models import Member

class MemberForm(ModelForm):
    class Meta:
        model = Member
        exclude = ('created', 'modified', 'user',)