# WhatsUpGold-to-Ansible
Automatically transfer WhatsUp Gold's Inventory to Ansible
## Prerequisites
1. All WhatsUp Gold groups to be transferred to Ansible should be under a static group.

Example:
```
Groups to be transferred (static)
  |-- Group 1 will be transferred (dynamic)
  |-- Group 2 will also be transferred (dynamic)

Group 3 will not be transferred
```
2. The Group description in WhatsUp Gold should be reserved for its Ansible's equivalent group name. 
![WhatsUp Gold Group Description](https://github.com/kahhong/WhatsUpGold-to-Ansible/blob/main/Capture.JPG?raw=true)
## What do you need to change
```
host = IP Address of the WhatsUp Gold Monitor
username = Swagger API's username
password = Swagger API's password

...

def get_groups():
    # Group id of 51 refers to all custom dynamic groups
    # To get the ids of other groups, send this url with an id of -2.
    groupid = The groupid of the static group containing all the groups to be transferred.
    
    ...
    
f = open(r'Absolute path of Ansible inventory file for output', "w")
```

## Others
You can schedule this script to run on a timely basis to ensure your Ansible's inventory stays updated as your WhatsUp Gold's inventory.
