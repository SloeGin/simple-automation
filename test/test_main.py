from stoa.sensors import Sensor
from stoa.constants import sensorDef
from stoa.controller import LogicController
from stoa.schedule import Schedule


def demo1():
    control = LogicController()

    s1 = Sensor(1, sensorDef.SENSOR_BINARY_SENSOR)
    s2 = Sensor(2, sensorDef.SENSOR_BINARY_SWITCH, "lamp 1")
    s3 = Sensor(3, sensorDef.SENSOR_MOTION, "motion")
    s4 = Sensor(4, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 2")
    s5 = Sensor(5, sensorDef.SENSOR_TEMPERATURE, "temperature")
    s6 = Sensor(6, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 3")
    s7 = Sensor(7, sensorDef.SENSOR_THERMOSTAT, "thermostat")
    s8 = Sensor(8, sensorDef.SENSOR_UNKNOWN, "UNKOWN")
    s11 = Sensor(11, sensorDef.SENSOR_BINARY_SENSOR, "door_1")
    s12 = Sensor(12, sensorDef.SENSOR_BINARY_SENSOR, "door_2")
    points_7 = [
        {"point_id": "3", "point_type": "9", "point_value": None},
        {"point_id": "4", "point_type": "12", "point_value": None},
        {"point_id": "6", "point_type": "10", "point_value": None},
        {"point_id": "1", "point_type": "8", "point_value": "25"}
    ]
    s7.load_point_list(points_7)

    control.add_sensor(s1)
    control.add_sensor(s2)
    control.add_sensor(s3)
    control.add_sensor(s4)
    control.add_sensor(s5)
    control.add_sensor(s6)
    control.add_sensor(s7)
    control.add_sensor(s8)
    control.add_sensor(s11)
    control.add_sensor(s12)

    rule_data = {
        "sensor": 1,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "zwave_set", "value": 1, "sensor": 2},
        "condition": {
            "left": {"method": "=wd=", "threshold": None, "sensor": 0},
            "logic": "and",
            "right": {"method": "=g=", "threshold": 20, "sensor": 5}
        }
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 1,
        "enabled": False,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "zwave_set", "value": 255, "sensor": 4}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 1,
        "enabled": True,
        "trigger": {"method": "match", "target": 1}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 8,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "zwave_set", "value": 255, "sensor": 1}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 9,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "zwave_set", "value": 255, "sensor": 2}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 3,
        "trigger": {"method": "match", "target": 1},
        "action": [
            {"method": "zwave_set", "value": 50, "sensor": 4},
            {"method": "zwave_set", "value": 50, "sensor": 6},
            {"method": "notify"}
        ],
        "condition": {"method": "=wd=", "threshold": None, "sensor": 0}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 11,
        "trigger": {"method": "match", "target": 1},
        "action": [
            {"method": "zwave_set", "value": 50, "sensor": 4},
            {"method": "zwave_set", "value": 50, "sensor": 6},
            {"method": "notify"}
        ],
        "condition": {"method": "=wd=", "threshold": None, "sensor": 0}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 11,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "zwave_set", "value": 255, "sensor": 2}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 5,
        "trigger": {"method": "rise", "target": 26},
        "action": [
            {"method": "zwave_set", "value": 1, "sensor": 7},
            {"method": "zwave_set", "value": 20, "sensor": 7,  "point": 3}
        ],
        "condition": {
            "left": {"method": "=wd=", "threshold": None, "sensor": "0"},
            "logic": "and",
            "right": {
                "left": {"method": "=ta=", "threshold": "1460289600", "sensor": "0"},
                "logic": "and",
                "right": {"method": "=tb=", "threshold": 1460325600, "sensor": 0}
            }
        }
    }
    control.add_rule(rule_data)

    rule_data = {
        "state": {
            "left": {"sensor": 11, "target": 1},
            "logic": "and",
            "right": {"sensor": 12, "target": 1}
        }
    }
    control.add_rule(rule_data)

    print(control)

    s5.update_value(28)
    s1.update_value(0)
    s3.update_value(0)
    s5.update_value(26)
    s1.update_value(1)
    s3.update_value(1)
    s5.update_value(27)
    s3.update_value(0)
    s1.update_value(0)
    s3.update_value(1)
    s5.update_value(28)
    control.get_sensor(1).update_value(1)

    # control.remove_rule(3, 0)

    # print(control)
    control.print_rules()
    #
    # rule_data = control.dump_rule(1)
    #
    # control.remove_rule(1, 0)
    # control.remove_rule(1, 0)
    #
    # control.add_rule(rule_data)
    # control.remove_sensor(2)
    #
    # control.enable_rule(1, 0)
    # control.disable_rule(1, 1)
    # print(control)
    # control.print_rules()

    print "-------------------------------"

    control.remove_sensor(6)

    print control
    control.print_rules()


def demo2():
    control = LogicController()

    s1 = Sensor(1, sensorDef.SENSOR_TEMPERATURE, "temperature")
    s2 = Sensor(2, sensorDef.SENSOR_BINARY_SWITCH, "heater")

    control.add_sensor(s1)
    control.add_sensor(s2)

    rule_data = {
        "sensor": 1,
        "enabled": False,
        "trigger": {"method": "fall", "target":19},
        "action": {"method": "zwave_set", "value": 255, "sensor": 2},
        "v.v.": True
    }
    control.add_rule(rule_data)

    print control

    control.enable_rule(1, 0)
    s1.update_value(20)
    s1.update_value(19)
    control.handle_data(sensor_id=1, value=18)
    control.handle_data(sensor_id=1, value=17)


def demo3():
    """
    {
        "action": {"method": "security_mode"},
        "weekdays": [
            {"enabled": True, "time": 1495051200, "value": 1},
            {"enabled": True, "time": 1495051260, "value": 0},
            {"enabled": True, "time": 1495051320, "value": 1},
            {"enabled": True, "time": 1495051380, "value": 0},
        ],
        "weekends": [
            {"enabled": True, "time": 1495058400, "value": 1},
            {"enabled": True, "time": 1495065600, "value": 0}
        ]
    }
    """
    sc = {
        "action": {"method": "security_mode"},
        "weekdays": [
            {"enabled": True, "time": 1494961200, "value": 1}, # 3 pm
            {"enabled": True, "time": 1494964800, "value": 0}  # 4 pm
        ],
        "weekends": [
            {"enabled": True, "time": 1495058400, "value": 1}, # 6 pm
            {"enabled": True, "time": 1495065600, "value": 0}  # 8 pm
        ]
    }

    sc = {
        "action": {"method": "zwave_set", "sensor":1},
        "Fri": [
            {"enabled": True, "time": 1494961200, "value": 1}, # 3 pm
            {"enabled": True, "time": 1494964800, "value": 0}  # 4 pm
        ],
        "Sun": [
            {"enabled": True, "time": 1495058400, "value": 1}, # 6 pm
            {"enabled": True, "time": 1495065600, "value": 0}  # 8 pm
        ]
    }

    s = Schedule(sc)
    print s

    for i in range(1494961000, 1494961500, 25):
        # wd 3pm Tue
        s.handle_data(i)
    for i in range(1494964600, 1494965100, 25):
        # wd 4pm Tue
        s.handle_data(i)
    for i in range(1495047200, 1495047900, 25):
        # wd 3pm Wed
        s.handle_data(i)
    for i in range(1495915000, 1495915400, 25):
        # we 4pm Sat
        s.handle_data(i)
    for i in range(1495929200, 1495929800, 25):
        # we 8pm Sat
        s.handle_data(i)


if __name__ == "__main__":
    demo3()


