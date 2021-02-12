import requests, json, datetime, yaml

# variable host, username and password is for authenticating swagger API
host = "192.168.20.4"
username = "admin"
password = "admin"

# Authentication url
mauthendpoint = "http://%s:9644/api/v1/token" % host


### Authenticate for Swagger API ###
def get_access_header(mauthendpoint, musername , mpassword):
    mgrant_type="password"
    mauthbody = {"grant_type":mgrant_type,"username": musername, "password":mpassword}
    r=requests.post(mauthendpoint, data=mauthbody, verify=False)
    r.raise_for_status()
    rjson=r.json()
    header = {"Authorization": "Bearer %s" % rjson["access_token"]}
    return header

### Send api call to swagger ###
def send_api_call(url):
    mdeviceios = url 
    access_header = get_access_header(mauthendpoint,username,password)
    r = requests.get(mdeviceios,headers=access_header,verify=False)
    r.raise_for_status()
    result = json.loads(r.text)
    return result

### Get all children groups in "All custom groups" group ###

def get_groups():
    # Group id of 51 refers to all custom dynamic groups
    # To get the ids of other groups, send this url with an id of -2.
    groupid = 51
    url = "http://%s:9644/api/v1/device-groups/%d/children" % (host, groupid)
    result = send_api_call(url)
    # Zip the group name and group id into a List and return it
    group_name = []
    group_id = []
    for i in result['data']['groups']:
        group_name.append(i['description'])
        group_id.append(i['id'])

    zippedlist = list(zip(group_name, group_id))
    return zippedlist

# Sample output:
#   [('All routers (dynamic group)', '3'), ('subnet_16', '46')]

### Get devices info of a group ###

def get_group_inventory(groupid):
    url = "http://%s:9644/api/v1/device-groups/%d/devices/-/config/template" % (host, groupid)
    result = send_api_call(url)
    return result

# Sample output:
#   {'paging': {'pageId': '0', 'size': 1}, 'data': {'deviceCount': 1, 'errors': [], 'templates': [{'templateId': '46', 'displayName': 'S2', 'deviceType': 'Cisco Switch', 'snmpOid': '1.3.6.1.4.1.9.1.1227', 'pollInterval': '', 'primaryRole': 'Switch', 'subRoles': ['Switch', 'Unix'], 'os': 'Cisco IOS', 'brand': 'Cisco', 'actionPolicy': '', 'note': 'This device was scanned by discovery on 12/31/2020 2:27:09 PM.', 'autoRefresh': 'True', 'credentials': [{'credentialType': 'SNMP v3', 'credential': 'skahhong'}, {'credentialType': 'SSH', 'credential': 'Cisco'}], 'interfaces': [{'defaultInterface': True, 'pollUsingNetworkName': False, 'networkAddress': '10.0.0.2', 'networkName': '10.0.0.2'}], 'attributes': [{'name': 'Contact', 'value': ''}, {'name': 'Description', 'value': 'Cisco IOS Software, vios_l2 Software (vios_l2-ADVENTERPRISEK9-M), Version 15.2(CML_NIGHTLY_20180619)FLO_DSGS7, EARLY DEPLOYMENT DEVELOPMENT BUILD, synced to  V152_6_0_81_E  Technical Support: http://www.cisco.com/techsupport  Copyright (c) 1986-2018 by Ci'}, {'name': 'FwVersion', 'value': 'Bootstrap program is IOSv'}, {'name': 'HwVersion', 'value': '1.0'}, {'name': 'Location', 'value': ''}, {'name': 'MACAddress', 'value': '0C:5B:CB:10:1C:00'}, {'name': 'MACAddressVendor', 'value': 'unknown'}, {'name': 'Model', 'value': 'Cisco Catalyst 3560X-48T-L,S Switch (WS-C3560X-48T-L,WS-C3560X-48T-S)'}, {'name': 'Name', 'value': 'S2'}, {'name': 'SerialNumber', 'value': '9I03RXYA7H2'}, {'name': 'Vendor', 'value': 'Cisco'}, {'name': 'Vendor_OS', 'value': ''}, {'name': 'Vendor_OSVersion', 'value': ''}], 'customLinks': [{'name': 'Browse', 'value': 'http://%Device.UrlAddress/'}], 'activeMonitors': [{'classId': 'd6d02d69-a418-483a-93ea-20dd2af2d135', 'name': 'Interface', 'argument': '1', 'comment': 'GigabitEthernet0/0 (10.0.0.2)'}, {'classId': 'd6d02d69-a418-483a-93ea-20dd2af2d135', 'name': 'Interface', 'argument': '17', 'comment': 'Null0'}, {'classId': '2655476e-36b0-455f-9cce-940b6f8e07bf', 'name': 'Ping', 'argument': '', 'comment': ''}], 'performanceMonitors': [{'classId': '3d199773-46ef-4cbb-b992-7076612c7668', 'name': 'Interface Utilization'}, {'classId': 'dacd2861-27d9-48e6-9e70-2016e794effe', 'name': 'Ping Latency and Availability'}], 'passiveMonitors': [], 'dependencies': [], 'applicationProfiles': [], 'layer2Data': '', 'groups': [{'parents': ['My Network'], 'name': 'Discovered Devices'}]}]}}

### Filter return data and return it ###

def process_inventory(json):
    z = []
    y = dict.fromkeys(['Device','DeviceType','OS','IPAddress'])
    for i in range(json['data']['deviceCount']):
        y['Device'] = json['data']['templates'][i]['displayName']
        y['DeviceType'] = json['data']['templates'][i]['deviceType']
        y['OS'] = json['data']['templates'][i]['os']
        for j in json['data']['templates'][i]['interfaces']:
            if (j['defaultInterface']):
                y['IPAddress'] = j['networkAddress']
        z.append(y.copy())
    return z

# Sample output:
#   [{'Device': 'tabletop.playground.com', 'DeviceType': 'Cisco Switch', 'OS': 'Cisco IOS', 'IPAddress': '10.0.0.10'}]

### "toyaml" is a dictionary file to be converted to yaml before writing to the file ###
toyaml = {} 
groups = get_groups()

### Send the actual api call and populate the "toyaml" dictionary  ###
for i in groups: # For every group
    toyaml.update({i[0]:{"hosts":{}}}) # Add group to dictionary
    processed_device_data = process_inventory(get_group_inventory(int(i[1]))) # Process the chunk which contains all the devices in that group

    for j in processed_device_data:
        # Update "toyaml" dictionary
        toyaml[i[0]]['hosts'].update({j['Device']:{"ansible_host":j["IPAddress"]}})
# Sample "toyaml" output:
#   {'unknown': {'hosts': {}}, 'All routers (dynamic group)': {'hosts': {'S1.playground.com': {'ansible_host': '192.168.20.130'}}}, 'subnet_16': {'hosts': {'S2': {'ansible_host': '10.0.0.2'}}}}

### Convert the dictionary to yaml and write to Ansible inventory directory ###
y = yaml.dump(toyaml)
f = open(r'/home/ansible/ansible/inventory/fromwug.yml', "w")
yaml.dump(toyaml,f)
f.close()

# Sample output:
#   All routers (dynamic group):
#   hosts:
#     S1.playground.com: {ansible_host: 192.168.20.130}
# subnet_16:
#   hosts:
#     S2: {ansible_host: 10.0.0.2}
# unknown:
#   hosts: {}
