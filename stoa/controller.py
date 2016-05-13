from stoa.actions import action_table, ActionGroup, ActionOre
from stoa.observers import Logic, Observer, Node
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
        if int(sensor_id) not in self._dict:
            raise IndexError("Sensor ID out of Range")
        return self._dict[int(sensor_id)]

    def update_sensor(self, value, sensor_id, point_id=None):
        self._dict[sensor_id].update_value(value, point_id)

    def add_trigger(self, sensor_id, trigger):
        # load trigger from json to controller
        if sensor_id is None:
            raise ValueError("Must provide sensor id!")
        if trigger is None:
            raise ValueError("No trigger in rule!")
        sensor = self._dict[sensor_id]
        if not sensor.is_triggerable():
            raise ValueError("Sensor {0} is not triggerable!".format(sensor_id))
        t = trigger_table[trigger["method"]](trigger["target"])
        index = sensor.add_trigger(copy(t))
        self._cur_trigger = sensor.get_trigger(index)
        return index

    def remove_trigger(self, sensor_id, index):
        sensor = self._dict[sensor_id]
        sensor.remove_trigger(index)

    def add_action(self, actions):
        if self._cur_trigger is None:
            print("No trigger on top")

        if actions is None:
            raise ValueError("No action in rule!")

        if isinstance(actions, ActionOre):
            self._cur_trigger(actions)
            self._cur_action = self._cur_trigger.get_action()
            return

        if isinstance(actions, list):
            action = ActionGroup()
            for item in actions:
                action.add_action(self._load_action(item))
        else:
            action = self._load_action(actions)

        self._cur_trigger.assign(copy(action))
        self._cur_action = self._cur_trigger.get_action()

    def _load_action(self, action):
        # add action from json to the current trigger
        if action["method"] == "default":
            value = load_value(action, "value")
            sensor = load_value(action, "sensor")
            point = load_value(action, "point")
            delay = load_value(action, "delay")
            tmo = load_value(action, "tmo")

            if not self._dict[sensor].is_actable():
                raise ValueError("Sensor {0} is not actable!".format(sensor))

            return action_table["default"](value, sensor, point, delay, tmo)

        if action["method"] == "notify":
            trigger = self._cur_trigger

            return action_table["notify"](trigger)

    def add_done(self):
        if self._cur_trigger and not self._cur_trigger.is_validated():
            self._cur_trigger.sensor.remove_trigger(None)
        self._cur_trigger = None
        self._cur_action = None

    def add_rule(self, rule):
        try:
            if isinstance(rule, list):
                for item in rule:
                    self._add_rule(item)
            else:
                self._add_rule(rule)
        except Exception as e:
            print("Failed adding rule: {0}".format(e))

    def _add_rule(self, rule):
        sensor = load_value(rule, "sensor")
        trigger = load_value(rule, "trigger")
        action = load_value(rule, "action")
        observer = load_value(rule, "observer")
        try:
            self.add_trigger(sensor, trigger)
            self.add_action(action)
            self.add_observer(observer)
        except Exception as e:
            print("Failed adding rule: {0}".format(e))
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
        if isinstance(observer, Node):
            self._cur_action.add_observer(observer)
            return

        o = self._load_ob(observer)
        if o:
            self._cur_action.add_observer(o)

    def dump_rules(self):
        for id in self._dict:
            sensor = self.get_sensor(id)
            if sensor.has_trigger():
                print("sensor_{0}.json".format(sensor.sensor_id))
                print(sensor.to_dict())

    def dump_rule(self, sensor_id):
        sensor = self.get_sensor(sensor_id)
        return sensor.to_dict()

    def handle_data(self, sensor_id, value, point=None):
        sensor = self._dict[sensor_id]
        sensor.update_value(value, point)
