from datetime import datetime
from stoa.sensors import Sensor


#########################
# Node object
#########################
class Node(object):
    _ID = 0

    def __init__(self):
        self.id = self._ID
        self.__class__._ID += 1

    def __call__(self):
        return False

    def check(self):
        return self.__call__()


#########################
# Rules for observer
#########################
TIME_FUZZ = 0


def weekday(value):
    time1 = datetime.fromtimestamp(value)
    return time1.weekday() < 5


def weekend(value):
    time1 = datetime.fromtimestamp(value)
    return time1.weekday() >= 5


def time_match(value, threshold):
    """time is matched in minute level"""
    time1 = datetime.fromtimestamp(value)
    time2 = datetime.fromtimestamp(threshold)

    if time1.hour == time2.hour:
        minute_delta = abs(time1.minute - time2.minute)
        if minute_delta <= TIME_FUZZ:
            return True
    return False


def time_before(value, threshold):
    """before a time in one day"""
    time1 = datetime.fromtimestamp(value)
    time2 = datetime.fromtimestamp(threshold)

    hour = time2.hour
    minute = time2.minute
    second = time2.second

    time2 = time1.replace(hour=hour, minute=minute, second=second)

    if time1 < time2:
        return True
    else:
        return False


def time_after(value, threshold):
    """after a time in one day"""
    time1 = datetime.fromtimestamp(value)
    time2 = datetime.fromtimestamp(threshold)

    hour = time2.hour
    minute = time2.minute
    second = time2.second

    time2 = time1.replace(hour=hour, minute=minute, second=second)

    if time1 > time2:
        return True
    else:
        return False


Condition = {
    "=g=": lambda x, y: x > y,
    "=l=": lambda x, y: x < y,
    "=e=": lambda x, y: x == y,
    "=ge=": lambda x, y: x >= y,
    "=le=": lambda x, y: x <= y,
    "=wd=": lambda x, y: weekday(x),
    "=we=": lambda x, y: weekend(x),
    "=wdm=": lambda x, y: weekday(x) and time_match(x, y),
    "=wem=": lambda x, y: weekend(x) and time_match(x, y),
    "=tm=": time_match,
    "=tb=": time_before,
    "=ta=": time_after
}


class Observer(Node):
    def __init__(self, rule, threshold, sensor, point=None):
        if not isinstance(sensor, Sensor):
            raise ValueError("Must have a valid sensor as input")
        super(Observer, self).__init__()
        self.rule = rule
        self.threshold = threshold
        self.sensor = sensor
        self.point = point

    def __call__(self):
        value = self.get_sensor()
        return Condition[self.rule](value, self.threshold)

    def get_sensor(self):
        if self.point is None:
            return self.sensor.get_value()
        else:
            return self.sensor.get_point(self.point)

    def __str__(self):
        return "Sensor:{sensor}(type:{type}) {rule} {threshold}".format(
            sensor=self.sensor.sensor_id,
            type=self.sensor.type,
            rule=self.rule,
            threshold=self.threshold
        )


#######################
# Rules for logic
#######################
Logic_table = {
    "and": lambda x, y: x and y,
    "or": lambda x, y: x or y,
    "xor": lambda x, y: (x and not y) or (not x and y)
}


class Logic(Node):
    def __init__(self, left, logic, right):
        super(Logic, self).__init__()
        self.left = left
        self.right = right
        self.logic = logic

    def link_left(self, left):
        """add left leaf"""
        self.left = left

    def link_right(self, right):
        """add right leaf"""
        self.right = right

    def __call__(self):
        if self.left is None or self.right is None:
            return False
        if self.right is None:
            return self.left()
        else:
            return Logic_table[self.logic](self.left(), self.right())

    def __str__(self):
        return "{0} {1} {2}".format(
            self.left, self.logic, self.right
        )

    def __repr__(self):
        return self.__str__()
