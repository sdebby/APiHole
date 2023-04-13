# Interface for using PiHole with API
import logging
import requests

logging.basicConfig(level=logging.INFO)

TotalURL='http://{0}/admin/api.php?{1}&auth={2}'

class PiHole():

    def GetSummery(IP:str,API:str):
        """
        Get PiHole summery
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        # TotalURL='http://'+IP+'/admin/api.php?summary&auth='+API
        try:
            global TotalURL
            resp = requests.get(url=TotalURL.format(IP,'summery',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans='ADS today:'+data['ads_percentage_today']+'%\n'+ \
            'Status '+data['status']
            return ans
        except:
            logging.error('Error connecting to PiHole')

    def GetVer(IP:str,API:str):
        """
        Get PiHole API version
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'versioni',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans='Version:'+data['version']
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
     
    def Disable(IP:str,API:str,Time:int):
        """
        Disable PiHole
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - Time: time to disable in sec, set to 0 for infinate time
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'disable='+str(Time),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            ans=data['status']
            return ans
        except:
            logging.error('Error connecting to PiHole')
        
    def GetTopItems(IP:str,API:str):
        """
        Get top 5 blocked/permitted items
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        TopNo=5
        try:
            resp = requests.get(url=TotalURL.format(IP,'topItems='+str(TopNo),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data
        except:
            logging.error('Error connecting to PiHole')
            
    def GetTopClients(IP:str,API:str):
        """
        Get top 5  client
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        TopNo=5
        try:
            resp = requests.get(url=TotalURL.format(IP,'topClients='+str(TopNo),API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data['top_sources']
        except:
            logging.error('Error connecting to PiHole')

    def GetTopClientsBlocked(IP:str,API:str):
        """
        Get top 5 blocked client
        - IP: the PiHole mashine URL
        - API: PiHole API key
        """
        TopNo=5
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
            resp = requests.get(url=TotalURL.format(IP,'enable',API))
            logging.info('Getting data from PiHole address '+IP)
            data=resp.json()
            return data
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

    def AddBlack(IP:str,API:str,Domain:str):
        """
        Add domain to black list
        - IP: the PiHole mashine URL
        - API: PiHole API key
        - Domain: domain to add to BLACK list
        Return True is sucsess
        """
        try:
            resp = requests.get(url=TotalURL.format(IP,'list=black&add='+Domain,API))
            logging.info('Getting data from PiHole address '+IP)
            return True
        except:
            logging.error('Error connecting to PiHole')
            return False