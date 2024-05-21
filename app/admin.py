# admin.py
from django.contrib import admin
from .models import Quiz

class QuizAdmin(admin.ModelAdmin):
    # Specify the fields to be displayed in the list view of the admin panel
    list_display = ('user', 'topic', 'score')
    
    # Optionally, you can also make the fields searchable
    search_fields = ('user__username', 'topic')

    # Optionally, you can add filters for the list view
    list_filter = ('topic',)

admin.site.register(Quiz, QuizAdmin)
