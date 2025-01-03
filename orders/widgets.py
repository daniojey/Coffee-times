from datetime import datetime, timedelta
from django import forms

# Виджет генерации времени для поля reservation_time
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


        if len(time_choices) == 0:
            time_choices.append(('01','01'))

        return time_choices
    
# Виджет генерации времени для поля booking_duration
class CustomBookingSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = self.generate_time_choices()

    
    def generate_time_choices(self):
        now = datetime.now()
        time_choices = []

        for hour in range(0, 4):
            for minute in range(0, 60, 15):
                    if hour <= 3:
                        if hour == 3 and minute > 0:
                            break
                        else:
                            time_str = f"{hour:02}:{minute:02}"
                            time_choices.append((time_str, time_str))

        return time_choices
