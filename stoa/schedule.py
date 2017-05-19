from .actions import action_table
from .condition import weekday

from datetime import datetime
import time

TIME_RESOLUTION = 60
DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

WEEKDAYS = "weekdays"
WEEKENDS = "weekends"


def is_wd_or_we(timestamp):
    if weekday(timestamp):
        return WEEKDAYS
    else:
        return WEEKENDS


def day_of_week(timestamp):
    time1 = datetime.fromtimestamp(timestamp)
    return DAYS_OF_WEEK[time1.weekday()]


def back_to_that_day(time1):
    timestamp = datetime.fromtimestamp(time1)
    hour = timestamp.hour
    minute = timestamp.minute
    second = timestamp.second
    time_fix = datetime.fromtimestamp(604645200)
    timestamp = time_fix.replace(hour=hour, minute=minute, second=second)
    return int(time.mktime(timestamp.timetuple()))


class Schedule(object):
    """
    {
      "action":{"method":"security_mode"},
      "weekdays":[
        {"enabled":true, "time":timestamp, "value":1},
        {"enabled":true, "time":timestamp, "value":0}
      ],
      "weekends":[
        {"enabled":true, "time":timestamp, "value":1},
        {"enabled":true, "time":timestamp, "value":0}
      ]
    }
    """
    def __init__(self, data):
        if not type(data) == dict:
            raise ValueError("Schedule need to be a dict")
        action = data.get("action")
        if not action:
            raise ValueError("Action in schedule must be defined")
        action_method = action.get("method")
        if not action_method:
            raise ValueError("Method in action must be defined")

        self.action = action_table[action_method](**action)
        self.schedule = dict()
        self.last_trigger_time = 0

        if {WEEKDAYS, WEEKENDS} & set(data):
            # This is a 5-2 schedule
            self.type = 2
            self.load_schedule(WEEKDAYS, data)
            self.load_schedule(WEEKENDS, data)
        elif set(DAYS_OF_WEEK) & set(data):
            self.type = 7
            for days in DAYS_OF_WEEK:
                self.load_schedule(days, data)

    def load_schedule(self, key_of_interest, data):
        schedule = data.get(key_of_interest)
        if not schedule:
            return None
        schedule_trigger = dict()
        for item in schedule:
            timestamp = back_to_that_day(item.get("time"))
            schedule_trigger[timestamp] = {"value": item.get("value"), "enabled": item.get("enabled")}
        self.schedule[key_of_interest] = schedule_trigger

    def handle_data(self, time_now):
        time_now = int(time_now) / TIME_RESOLUTION * TIME_RESOLUTION
        if self.type == 2:
            dow = is_wd_or_we(time_now)
            self.check_schedule(dow, time_now)
        elif self.type == 7:
            dow = day_of_week(time_now)
            self.check_schedule(dow, time_now)

    def check_schedule(self, dow, time_now):
        schedule_table = self.schedule.get(dow)
        if not schedule_table:
            return False
        if self.last_trigger_time == time_now:
            return False
        time_that_day = back_to_that_day(time_now)
        if time_that_day in schedule_table:
            if schedule_table[time_that_day].get("enabled"):
                self.action.active_once(schedule_table[time_that_day].get("value"))
                self.last_trigger_time = time_now
                return True
            return False
        return False

    def __str__(self):
        res = self.schedule
        return str(res)

    def __repr__(self):
        return self.__str__()
