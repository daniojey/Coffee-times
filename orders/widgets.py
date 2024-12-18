from datetime import datetime, timedelta
from django import forms

class CustomTimeSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = self.generate_time_choices()

    def generate_time_choices(self):
        now = datetime.now()
        time_choices = []

        start_hour = now.hour
        start_minute = now.minute

        for hour in range(0, 24):
            for minute in range(0, 60, 30):
                if hour > start_hour or (hour == start_hour and minute > start_minute):
                    time_str=f"{hour:02}:{minute:02}"
                    time_choices.append((time_str, time_str))

    
        return time_choices