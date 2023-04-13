from APiHole import PiHole

PiHoleAPI='PiHole_API'
PiIP='pi.hole'

# get PiHole summary
print(PiHole.GetSummary(PiIP,PiHoleAPI))

# get PiHole status
print(PiHole.GetStatus(PiIP,PiHoleAPI))

# get PiHole gravisy status
print(PiHole.GetGravity(PiIP,PiHoleAPI))

# get PiHole top items, split and convert to list
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

# enable PiHole
print(PiHole.Enable(PiIP,PiHoleAPI))

# disable PiHole for 2 sec
print(PiHole.Disable(PiIP,PiHoleAPI,2))

# Get top clients
print(PiHole.GetTopClients(PiIP,PiHoleAPI))

# Add google.com to white list
print(PiHole.AddWhite(PiIP,PiHoleAPI,'google.com'))

# Add google.com to block list
print(PiHole.AddBlock(PiIP,PiHoleAPI,'google.com'))

# Print API version (good for testing communication)
print(PiHole.GetVer(PiIP))

# Print recent blocked domain
print(PiHole.GetRecentBlocked(PiIP,PiHoleAPI))

# Print destinations in %
print(PiHole.GetDestination(PiIP,PiHoleAPI))

# Print query types in %
print(PiHole.GetQueryTypes(PiIP,PiHoleAPI))

# Print clients names
print(PiHole.GetClientNames(PiIP,PiHoleAPI))

# Print data of clients over time
print(PiHole.GetOverTimeDataClients(PiIP,PiHoleAPI))

# Print pi hole DNS port
print(PiHole.GetDnsPort(PiIP,PiHoleAPI))

# Print pi hole chche info
print(PiHole.GetCacheInfo(PiIP,PiHoleAPI))

# Print pi hole data of 10 min 
print(PiHole.GetOverTimeData10mins(PiIP,PiHoleAPI))