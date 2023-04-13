# Interface for using PiHole with API
import logging
import requests

logging.basicConfig(level=logging.INFO)

TotalURL='http://{0}/admin/api.php?{1}&auth={2}'
TotalURLWOa='http://{0}/admin/api.php?{1}'

class PiHole():

    def GetSummary(IP:str,API:str):
        """
        Get PiHole summary
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'summary',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            data.pop('gravity_last_updated')
            data.pop('status')
            # resultList = list(data.items())
            # resultList.pop(-1)
            # ans='ADS today:'+data['ads_percentage_today']+'%\n'+ 'Status '+data['status']
            return data
        except:
            logging.error('Error connecting to PiHole')

    def GetStatus(IP:str,API:str):
        """
        Get PiHole status
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'status',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans='Status: '+data['status']
            return ans
        except:
            logging.error('Error connecting to PiHole')

    def GetGravity(IP:str,API:str):
        """
        Get PiHole gravity status
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'summary',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['gravity_last_updated']
        except:
            logging.error('Error connecting to PiHole')

    def GetVer(IP:str):
        """
        Get PiHole API version
        - IP: the PiHole mashine URL
        """
        try:
            TotalURLVer='http://{0}/admin/api.php?{1}'
            resp = requests.get(url=TotalURLWOa.format(IP,'version'))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans='Version: '+str(data['version'])
            return ans
        except:
            logging.error('Error connecting to PiHole')

    def Enable(IP:str,API:str):
        """
        Enable PiHole
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'enable',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans=data['status']
            return ans
        except:
            logging.error('Error connecting to PiHole')
     
    def Disable(IP:str,API:str,Time:int=0):
        """
        Disable PiHole
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - Time: time to disable in sec, set to 0 for infinate time
            - Default value is 0
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'disable='+str(Time),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans=data['status']
            return ans
        except:
            logging.error('Error connecting to PiHole')
        
    def GetTopItems(IP:str,API:str,TopNo:int=5):
        """
        Get top blocked/permitted items
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - TopNo: The no of top item to display
            - Default value is 5
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'topItems='+str(TopNo),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data
        except:
            logging.error('Error connecting to PiHole')
            
    def GetTopClients(IP:str,API:str,TopNo:int=5):
        """
        Get top client
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - TopNo: The no of top item to display
            - Default value is 5
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'topClients='+str(TopNo),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['top_sources']
        except:
            logging.error('Error connecting to PiHole')

    def GetTopClientsBlocked(IP:str,API:str,TopNo:int=5):
        """
        Get top blocked client
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - TopNo: The no of top item to display
            - Default value is 5
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'topClientsBlocked='+str(TopNo),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['top_sources_blocked']
        except:
            logging.error('Error connecting to PiHole')

    def GetRecentBlocked(IP:str,API:str):
        """
        Get recent block domain
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'recentBlocked',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.content
            return data.decode("utf-8")
        except:
            logging.error('Error connecting to PiHole')
    
    def GetDestination(IP:str,API:str):
        """
        Get destinations in %
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'getForwardDestinationNames',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['forward_destinations']
        except:
            logging.error('Error connecting to PiHole')
            
    def GetQueryTypes(IP:str,API:str):
        """
        Get query types in %
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'getQueryTypes',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['querytypes']
        except:
            logging.error('Error connecting to PiHole')
                  
    def GetCacheInfo(IP:str,API:str):
        """
        Get cache info
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'getCacheInfo',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['cacheinfo']
        except:
            logging.error('Error connecting to PiHole')
            
    def GetClientNames(IP:str,API:str):
        """
        Get clients names
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'getClientNames',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['clients']
        except:
            logging.error('Error connecting to PiHole')

    def GetOverTimeDataClients(IP:str,API:str):
        """
        Get data of clients over time
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'overTimeDataClients',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data
        except:
            logging.error('Error connecting to PiHole')
   
    def GetOverTimeData10mins(IP:str,API:str):
        """
        Get data of blocked/total in last 10 min 
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'overTimeData10mins',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data
        except:
            logging.error('Error connecting to PiHole')
        
    def GetDnsPort(IP:str,API:str):
        """
        Get DNS port
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'dns-port',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()['dns-port']
            ans= 'DNS-Port:'+str(data)
            return ans
        except:
            logging.error('Error connecting to PiHole')
        
    def AddWhite(IP:str,API:str,Domain:str):
        """
        Add domain to white list
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - Domain: domain to add to WHITE list
        Return True is sucsess
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'list=white&add='+Domain,API))
            logging.info('Getting data from PiHole address '+IP)
            return True
        except:
            logging.error('Error connecting to PiHole')
            return False

    def AddBlock(IP:str,API:str,Domain:str):
        """
        Add domain to block list
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - Domain: domain to add to BLOCK list
        Return True is sucsess
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'list=black&add='+Domain,API))
            logging.info('Getting data from PiHole address '+IP)
            return True
        except:
            logging.error('Error connecting to PiHole')
            return False