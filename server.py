from flask import Flask, request, abort
import json
from os import path
from os import remove
import random
import string
import time

app = Flask(__name__)

# TODO fix so that deployments does not overwrite its self

def randomStr(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def throwError(errorName):
    with open(errorName + "Error.json", "r") as errors:
        return json.loads(errors.read()), 200


def project(jsonArray):
    open(jsonArray["project"] + ".json", "w").write(str(jsonArray["data"]))
    return '{"success", "true"}', 200


# example command  "{\"action\": {\"deployments\": \"update\"}}"
def action(jsonArray):
    # grabbing the key and value
    for key, value in jsonArray["action"].items():
        if value == "update":
            with open(key + ".json") as jsonData:
                return jsonData.read().replace("'", '"'), 200
        elif key == "addDevice":
            if path.exists("devices.json") and open("devices.json", "r").read() != "":
                with open("devices.json") as devicesJson:
                    devices = json.loads(devicesJson.read())
                    for device in devices["devices"]:
                        print("device", device)
                        if "*" + value + "*" in device:
                            return throwError("addDevice")
                    value = "*" + value + "*"
                    devices["devices"].append({str(value): [False, randomStr(32)]})
                json.dump(devices, open("devices.json", "w"))
                print(str(json.loads(open("devices.json", "r").read())["devices"]))
                return str(json.loads(open("devices.json", "r").read())["devices"]), 200
            else:
                with open("devices.json", "w+") as devicesJson:
                    devicesJson.write(
                        '{"devices": [{"' + str("*" + value + "*") + '": [false, "' + randomStr(32) + '"]}]}')
                print(str(json.loads(open("devices.json", "r").read())["devices"]))
                return str(json.loads(open("devices.json", "r").read())["devices"]), 200
        elif key == "addDeployment":
            if path.exists("deployments.json") and open("deployments.json", "r").read() != "":
                with open("deployments.json") as devicesJson:
                    devices = json.loads(devicesJson.read())
                    for device in devices["deployments"]:
                        print("deployments", device)
                        if "*" + value + "*" in device:
                            return throwError("addDeployment")
                    value = "*" + value + "*"
                    devices["deployments"].append({str(value): [False, randomStr(32)]})
                json.dump(devices, open("deployments.json", "w"))
                print(str(json.loads(open("deployments.json", "r").read())["deployments"]))
                return str(json.loads(open("deployments.json", "r").read())["deployments"]), 200
            else:
                with open("deployments.json", "w+") as devicesJson:
                    devicesJson.write(
                        '{"deployments": [{"' + str("*" + value + "*") + '": [false, "' + randomStr(32) + '"]}]}')
                print(str(json.loads(open("deployments.json", "r").read())["deployments"]))
                return str(json.loads(open("deployments.json", "r").read())["deployments"]), 200


# example command
def deleteItem(jsonArray):
    for key, value in jsonArray["delete"].items():
        with open(key + ".json") as jsonFile:
            if value == "*":
                remove(key + "json")
            else:
                jsonData = json.load(jsonFile)
                jsonData["key"] = ""
                json.dump(jsonFile, jsonData)
    return '{"success", "true"}', 200


# example command
def programCheckIn(jsonArray):
    print(jsonArray)
    programsJson = json.load(open("programs.json")) if path.exists("programs.json") else {}
    programsJson[jsonArray["programCheckIn"]] = str(round(time.time() * 1000))
    with open("programs.json", "w") as writeProgramsFile:
        json.dump(programsJson, writeProgramsFile)
    return '{"success", "true"}', 200


# example command
def autoDeploymentEngine(jsonArray):
    if path.exists("AutoDeploymentEngine.json"):
        with open("AutoDeploymentEngine.json", "r") as jsonFile:
            jsonData = json.load(jsonFile)
            for i, server in enumerate(jsonData["servers"]):
                for serverName, actions in server.items():
                    print(list(jsonArray.values())[0])
                    if serverName == list(jsonArray.values())[0]:
                        jsonResponse = jsonData["servers"][i][serverName]
                        jsonData["servers"][i][serverName] = []
                        with open("AutoDeploymentEngine.json", "w") as jsonFileW:
                            json.dump(jsonData, jsonFileW)
                        return json.dumps(jsonResponse), 200
    return '{"actions": "none"}', 200


# example command "{\"addAutoDeploymentEngineCommand\": {\"server\": {\"serverName\": {\"start\":  \"git@github.com:Catalyze326/Microcenter-Scraper.git\"}}}}"
def addAutoDeploymentEngineCommand(jsonArray):
    jsonArray = jsonArray["addAutoDeploymentEngineCommand"]
    if path.exists("AutoDeploymentEngine.json"):
        if open("AutoDeploymentEngine.json", "r").read() != "":
            with open("AutoDeploymentEngine.json", "r") as jsonFile:
                jsonData = json.load(jsonFile)
                with open("AutoDeploymentEngine.json", "w") as jsonFile:
                    for sentServerName, sentCommand in jsonArray["server"].items():
                        for i, server in enumerate(jsonData["servers"]):
                            print(server)
                            for j, (serverName, actions) in enumerate(server.items()):
                                if sentServerName == serverName:
                                    jsonData["servers"][i][serverName].append(sentCommand)
                                    json.dump(jsonData, jsonFile)
                                    return json.dumps(jsonData["servers"][i][serverName]), 200
    jsonData = {}
    with open("AutoDeploymentEngine.json", "w") as jsonFile:
        print(jsonArray["server"].items())
        for key, value in jsonArray["server"].items():
            jsonData["servers"] = [{key: [value]}]
            json.dump(jsonData, jsonFile)
            return jsonData, 200
    return {"actions": "none"}, 200


@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        jsonArray = json.loads(str(request.json).replace("'", '"'))
        print(jsonArray)
        if "project" in jsonArray:
            return project(jsonArray)
        elif "action" in jsonArray:
            return action(jsonArray)
        elif "programCheckIn" in jsonArray:
            return programCheckIn(jsonArray)
        elif "delete" in jsonArray:
            return deleteItem(jsonArray)
        elif "addAutoDeploymentEngineCommand" in jsonArray:
            return addAutoDeploymentEngineCommand(jsonArray)
        elif "AutoDeploymentEngine" in jsonArray:
            return autoDeploymentEngine(jsonArray)
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=556)
