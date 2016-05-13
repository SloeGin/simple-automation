from stoa.sensors import Sensor
from stoa.constants import sensorDef
from stoa.controller import LogicController


if __name__ == "__main__":
    control = LogicController()

    s1 = Sensor(1, sensorDef.SENSOR_BINARY_SENSOR, "door")
    s2 = Sensor(2, sensorDef.SENSOR_BINARY_SWITCH, "lamp 1")
    s3 = Sensor(3, sensorDef.SENSOR_MOTION, "motion")
    s4 = Sensor(4, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 2")
    s5 = Sensor(5, sensorDef.SENSOR_TEMPERATURE, "temperature")
    s6 = Sensor(6, sensorDef.SENSOR_MULTILEVEL_SWITCH, "lamp 3")
    s7 = Sensor(7, sensorDef.SENSOR_THERMOSTAT, "thermostat")
    points_7 = [
        {"point_id": "3", "point_type": "9", "point_value": None},
        {"point_id": "4", "point_type": "12", "point_value": None},
        {"point_id": "6", "point_type": "10", "point_value": None},
        {"point_id": "1", "point_type": "8", "point_value": "16777241"}
    ]
    s7.load_point_list(points_7)

    control.add_sensor(s1)
    control.add_sensor(s2)
    control.add_sensor(s3)
    control.add_sensor(s4)
    control.add_sensor(s5)
    control.add_sensor(s6)
    control.add_sensor(s7)

    rule_data = {
        "sensor": 1,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "default", "value": 1, "sensor": 2},
        "observer": {
            "left": {"method": "=wd=", "threshold": None, "sensor": 0},
            "logic": "and",
            "right": {"method": "=g=", "threshold": 20, "sensor": 5}
        }
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 1,
        "trigger": {"method": "match", "target": 1},
        "action": {"method": "default", "value": 255, "sensor": 4}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 3,
        "trigger": {"method": "match", "target": 1},
        "action": [
            {"method": "default", "value": 50, "sensor": 4},
            {"method": "default", "value": 50, "sensor": 6},
            {"method": "notify"}
        ],
        "observer": {"method": "=wd=", "threshold": None, "sensor": 0}
    }
    control.add_rule(rule_data)

    rule_data = {
        "sensor": 5,
        "trigger": {"method": "rise", "target": 26},
        "action": [
            {"method": "default", "value": 1, "sensor": 7},
            {"method": "default", "value": 20, "sensor": 7,  "point": 3}
        ],
        "observer": {
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
    s1.update_value(1)

    control.remove_trigger(3, 0)

    print(control)
    control.dump_rules()

    rule_data = control.dump_rule(1)

    control.remove_trigger(1, 0)
    control.remove_trigger(1, 0)

    control.add_rule(rule_data)

    print(control)
