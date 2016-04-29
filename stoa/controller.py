from stoa.actions import action_table, ActionGroup
from stoa.observers import Logic, Observer
from stoa.triggers import trigger_table
from stoa.sensors import Sensor, Clock
from copy import deepcopy as copy


def load_value(x, y):
    return x[y] if y in x else None


class LogicController(object):
    def __init__(self):
        self._dict = dict()
        self._dict[0] = Clock(0, 0, "clock")
        self._cur_action = None
        self._cur_trigger = None

    def list(self):
        return self._dict

    def __iter__(self):
        return iter(self._dict)

    def add_sensor(self, sensor):
        if isinstance(sensor, Sensor):
            if sensor.sensor_id == 0:
                raise ValueError("Fatal error: cannot overwrite system clock")
            if sensor.sensor_id in self._dict:
                raise ValueError("Sensor ID exists!")
            self._dict[sensor.sensor_id] = sensor
        else:
            try:
                if sensor["id"] == 0:
                    raise ValueError("Fatal error: cannot overwrite system clock")
                if sensor["id"] in self._dict:
                    raise ValueError("Sensor ID exists!")
                new_sensor = Sensor(sensor["id"], sensor["type"], sensor["name"])
                if "points" in sensor:
                    for point in sensor["points"]:
                        new_sensor.update_point(point)
                self._dict[sensor["id"]] = new_sensor
            except:
                print("Wrong sensor format")

        return True

    def __str__(self):
        res = "<Controller>\n"
        for i in (self.get_sensor(x) for x in self):
            res += str(i)
        return res

    def get_sensor(self, sensor_id):
        return self._dict[int(sensor_id)]

    def update_sensor(self, value, sensor_id, point_id=None):
        self._dict[sensor_id].update_value(value, point_id)

    def add_trigger(self, sensor_id, trigger):
        # load trigger from json to controller
        sensor = self._dict[sensor_id]
        t = trigger_table[trigger["method"]](trigger["target"])
        sensor.add_trigger(copy(t))
        self._cur_trigger = sensor.get_last_trigger()

    def add_action(self, actions):
        if isinstance(actions, list):
            action = ActionGroup()
            for item in actions:
                action.add_action(self._load_action(item))
        else:
            action = self._load_action(actions)

        self._cur_trigger.assign(copy(action))
        self._cur_action = self._cur_trigger.get_action()

    @staticmethod
    def _load_action(action):
        # add action from json to the current trigger
        value = load_value(action, "value")
        sensor = load_value(action, "sensor")
        point = load_value(action, "point")
        delay = load_value(action, "delay")
        tmo = load_value(action, "tmo")

        return action_table[action["method"]](value, sensor, point, delay, tmo)

    def add_done(self):
        self._cur_trigger = None
        self._cur_action = None

    def add_rule(self, rule):
        sensor = load_value(rule, "sensor")
        trigger = load_value(rule, "trigger")
        action = load_value(rule, "action")
        observer = load_value(rule, "observer")
        self.add_trigger(sensor, trigger)
        self.add_action(action)
        self.add_observer(observer)
        self.add_done()

    def _load_ob(self, observer):
        if observer is None:
            return None
        if "method" in observer:
            method = load_value(observer, "method")
            threshold = load_value(observer, "threshold")
            sensor = load_value(observer, "sensor")
            point = load_value(observer, "point")

            return Observer(method, threshold, self.get_sensor(sensor), point)
        elif "logic" in observer:
            left = load_value(observer, "left")
            logic = load_value(observer, "logic")
            right = load_value(observer, "right")

            return Logic(self._load_ob(left), logic, self._load_ob(right))
        else:
            return None

    def add_observer(self, observer):
        o = self._load_ob(observer)
        if o:
            self._cur_action.add_observer(o)
