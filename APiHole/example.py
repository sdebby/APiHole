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
Items=PiHole.GetTopItems(PiIP,PiHoleAPI)
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

# Print API version (good for testing communication)
print(PiHole.GetVer(PiIP))