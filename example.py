from APiHole import PiHole

PiHoleAPI='06b5b22528c72b4f6162a797cb029a4ff21202469673c89e5383d0170da0a27e'
PiIP='192.168.1.9'

# get PiHole summery
print(PiHole.GetSummery(PiIP,PiHoleAPI))

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