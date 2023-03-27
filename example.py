from APiHole import PiHole

PiHoleAPI='06b5b22528c72b4f6162a797cb029a4ff21202469673c89e5383d0170da0a27e'
PiIP='192.168.1.9'

print(PiHole.GetSummery(PiIP,PiHoleAPI))
Items=PiHole.GetTopItems(PiIP,PiHoleAPI)
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

# print(PiHole.Disable(PiIP,PiHoleAPI,0))

print(PiHole.Enable(PiIP,PiHoleAPI))
print(PiHole.GetTopClients(PiIP,PiHoleAPI))