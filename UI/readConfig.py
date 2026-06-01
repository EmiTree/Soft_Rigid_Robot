import json

with open("config.json", "r") as jsonfile: 
    configValues = json.load(jsonfile)

kp = configValues['kp']
ki = configValues['ki']
kd = configValues['kd']
setpoint = configValues['setpoint']

print(f"kp {kp} setpoint {setpoint}")
print(configValues)