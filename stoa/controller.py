from .actions import action_table, ActionGroup, ActionOre
from .condition import Gate, Condition, ConditionOre
from .triggers import trigger_table
from .sensors import Sensor, Clock
from copy import deepcopy


# TODO: Need a state controller for case "if Door A or Door B opens, turn light on otherwise turn in off".
class LogicController(object):
    def __init__(self):
        self.sensor_dict = dict()
        self.sensor_dict[0] = Clock(0, 0, "clock")
        self.schedule_list = []
        self._cur_trigger = None

    def list(self):
        return self.sensor_dict

    def __iter__(self):
        return iter(self.sensor_dict)

    def __str__(self):
        res = "<Controller>\n"
        for i in (self.get_sensor(x) for x in self):
            res += str(i)
        return res

    def add_sensor(self, sensor):
        if isinstance(sensor, Sensor):
            if sensor.sensor_id == 0:
                raise ValueError("Fatal error: cannot overwrite system clock")
            if sensor.sensor_id in self.sensor_dict:
                raise ValueError("Sensor ID exists!")
            self.sensor_dict[sensor.sensor_id] = sensor
        else:
            try:
                if sensor["id"] == 0:
                    raise ValueError("Fatal error: cannot overwrite system clock")
                if sensor["id"] in self.sensor_dict:
                    raise ValueError("Sensor ID exists!")
                new_sensor = Sensor(sensor["id"], sensor["type"], sensor["name"])
                if "points" in sensor:
                    for point in sensor["points"]:
                        new_sensor.update_point(point)
                self.sensor_dict[sensor["id"]] = new_sensor
            except:
                print "Wrong sensor format"

        return True

    def remove_sensor(self, sensor_id):
        try:
            if sensor_id == 0:
                raise ValueError("Fatal error: cannot overwrite system clock")
            if sensor_id not in self.sensor_dict:
                raise KeyError("Sensor ID not exists!")
            self.sensor_dict.pop(sensor_id)
            self.remove_trigger_by_action_sensor(sensor_id)
        except Exception as e:
            print e

    def get_sensor(self, sensor_id):
        if int(sensor_id) not in self.sensor_dict:
            raise KeyError(int(sensor_id))
        return self.sensor_dict[int(sensor_id)]

    def get_rules_from_sensor(self, sensor_id):
        if not self.sensor_dict.has_key(sensor_id):
            return None
        return self.sensor_dict[int(sensor_id)].get_triggers()

    def remove_trigger_by_action_sensor(self, sensor_id):
        for sensor in self.sensor_dict:
            rule = self.get_rules_from_sensor(sensor)
            if not rule:
                continue
            for index, item in enumerate(rule):
                if item.get_action().has_sensor(sensor_id):
                    item.sensor.remove_trigger(index)

    def add_trigger(self, sensor_id, trigger):
        # load trigger from json to controller
        if sensor_id is None:
            raise ValueError("Must provide sensor id!")
        if trigger is None:
            raise ValueError("No trigger in rule!")
        sensor = self.sensor_dict[sensor_id]
        if not sensor.is_triggerable():
            raise ValueError("Sensor {0} is not triggerable!".format(sensor_id))
        t = trigger_table[trigger["method"]](trigger["target"])
        index = sensor.add_trigger(deepcopy(t))
        self._cur_trigger = sensor.get_trigger(index)
        return index

    def remove_rule(self, sensor_id, index):
        sensor = self.sensor_dict[sensor_id]
        sensor.remove_trigger(index)

    def disable_rule(self, sensor_id, index):
        sensor = self.sensor_dict[sensor_id]
        sensor.disable_trigger(index)

    def enable_rule(self, sensor_id, index):
        sensor = self.sensor_dict[sensor_id]
        sensor.enable_trigger(index)

    def add_action(self, actions):
        if self._cur_trigger is None:
            print "No trigger on top"

        if actions is None:
            raise ValueError("No action in rule!")

        if isinstance(actions, ActionOre):
            self._cur_trigger.assign_action(actions)
            return

        if isinstance(actions, list):
            action = ActionGroup()
            for item in actions:
                action.add_action(self._load_action(item))
        else:
            action = self._load_action(actions)

        self._cur_trigger.assign_action(deepcopy(action))

    def _load_action(self, action):
        # add action from json to the current trigger
        if action["method"] == "zwave_set":
            sensor = action.get("sensor")
            if not self.sensor_dict[sensor].is_actable():
                raise ValueError("Sensor {0} is not actable!".format(sensor))
            return action_table["zwave_set"](action)

        if action["method"] == "notify":
            trigger = self._cur_trigger
            return action_table["notify"](trigger)

    def add_done(self):
        if self._cur_trigger and not self._cur_trigger.is_validated():
            self._cur_trigger.sensor.remove_trigger(None)
        self._cur_trigger = None

    def add_rule(self, rule):
        try:
            if isinstance(rule, list):
                for item in rule:
                    if "sensor" in item:
                        self._add_rule(item)
                    elif "state" in item:
                        self._add_lsm(item)
                    else:
                        print "Invalidate Rule"
            else:
                if "sensor" in rule:
                    self._add_rule(rule)
                elif "state" in rule:
                    self._add_lsm(rule)
                else:
                    print "Invalidate Rule"
        except Exception as e:
            print "Failed adding rule: {0}".format(e)

    def _add_lsm(self, rule):
        pass

    def _add_rule(self, rule):
        sensor = rule.get("sensor")
        trigger = rule.get("trigger")
        action = rule.get("action")
        condition = rule.get("condition")
        enabled = True if "enabled" not in rule else rule["enabled"]
        try:
            self.get_sensor(sensor)
            self.add_trigger(sensor, trigger)
            self.add_action(action)
            self.add_condition(condition)
            if enabled:
                self._cur_trigger.enable()
            else:
                self._cur_trigger.disable()
        except KeyError as e:
            print "Failed adding rule: Sensor {0} not exists!".format(e)
        except Exception as e:
            print "Failed adding rule: {0}".format(e)
        self.add_done()

    def _load_ob(self, condition):
        if condition is None:
            return None
        if "method" in condition:
            method = condition.get("method")
            threshold = condition.get("threshold")
            sensor = condition.get("sensor")
            point = condition.get("point")
            return Condition(method, threshold, self.get_sensor(sensor), point)
        elif "logic" in condition:
            left = condition.get("left")
            logic = condition.get("logic")
            right = condition.get("right")
            return Gate(self._load_ob(left), logic, self._load_ob(right))
        else:
            return None

    def add_condition(self, condition):
        if isinstance(condition, ConditionOre):
            self._cur_trigger.add_condition(condition)
            return

        o = self._load_ob(condition)
        if o:
            self._cur_trigger.add_condition(o)

    def print_rules(self):
        for sensor_id in self.sensor_dict:
            sensor = self.get_sensor(sensor_id)
            if sensor.has_trigger():
                print "sensor_{0}.json".format(sensor.sensor_id)
                print sensor.to_dict()

    def dump_rule(self, sensor_id):
        sensor = self.get_sensor(sensor_id)
        return sensor.to_dict()

    def handle_data(self, sensor_id, value, point=None):
        sensor = self.sensor_dict[sensor_id]
        sensor.update_value(value, point)
