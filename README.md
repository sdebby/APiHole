# APiHole

This is an easy python API module for comunicating with Pi Hole through API.
Works with AdminLTE v. 3

## Install:

```bash
pip install APiHole
```

## Get your Pi Hole API key from here:

```bash
sudo cat /etc/pihole/setupVars.conf | grep PASSWORD
```

## Usage
```python
from APiHole import PiHole

PiHoleAPI='your pi hole API key'
PiIP='your pi hole IP'

# Print API version (good for testing communication), (return string)
print(PiHole.GetVer(PiIP))

# get PiHole summary , (return dict)
PiHole.GetSummary(PiIP,PiHoleAPI)

# get PiHole gravity status , (return dict)
print(PiHole.GetGravity(PiIP,PiHoleAPI))

# get PiHole status, (return string)
PiHole.GetStatus(PiIP)

# get PiHole 7 top items, split and convert to list (return dict)
Items=PiHole.GetTopItems(PiIP,PiHoleAPI,7)
if not len(Items) == 0:
    ItemsTop=Items['top_queries']
    resultListTOP = list(ItemsTop.items())
    rtnTOP=[]
    ItemsADS=Items['top_ads']
    resultListADS = list(ItemsTop.items())
    rtnTOP=[]
    rtnADS=[]
    for l in range(len(resultListTOP)):
        rtnTOP.append(str(resultListTOP[l][0])+' : '+str(resultListTOP[l][1]))
        rtnADS.append(str(resultListADS[l][0])+' : '+str(resultListADS[l][1]))

    print('top_queries\n'+str(rtnTOP))
    print('top_ads\n'+str(rtnADS))

# enable PiHole (return string)
PiHole.Enable(PiIP,PiHoleAPI)

# disable PiHole for 2 sec (return string)
PiHole.Disable(PiIP,PiHoleAPI,2)

# Get top clients (return string)
PiHole.GetTopClients(PiIP,PiHoleAPI)

# Add google.com to white list (return boolean)
PiHole.AddWhite(PiIP,PiHoleAPI,'google.com')

# Add google.com to block list (return boolean)
PiHole.AddBlack(PiIP,PiHoleAPI,'google.com')

# get recent blocked domain, (return string)
PiHole.GetRecentBlocked(PiIP,PiHoleAPI)

# get destinations in %, (return dict)
PiHole.GetDestination(PiIP,PiHoleAPI)

# get query types in %, (return dict)
PiHole.GetQueryTypes(PiIP,PiHoleAPI)

# get clients names, (return dict)
PiHole.GetClientNames(PiIP,PiHoleAPI)

# get data of clients over time, (return dict)
PiHole.GetOverTimeDataClients(PiIP,PiHoleAPI)

# get pi hole DNS port, (return string)
PiHole.GetDnsPort(PiIP,PiHoleAPI)

# get pi hole chche info, (return dict)
PiHole.GetCacheInfo(PiIP,PiHoleAPI)

# get pi hole data of 10 min 
PiHole.GetOverTimeData10mins(PiIP,PiHoleAPI)
```
### TODOs


## Feedback

If you have any feedback, please reach out to us at shmulik.debby@gmail.com
