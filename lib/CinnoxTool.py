import logging

import requests
import yaml
import ssl
import urllib.request
from .loginEncrypt import passwordEncryption

class CinnoxTool:
    def __init__(self, env):
        self.s = requests.Session()
        self.config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
        # env = random.choice(self.config['env'].keys())
        # env = self.config['env']
        self.Base_URL = self.config['env'][env]['Base_URL']
        self.appID = self.config['env'][env]['appID']
        self.AppToken = self.config['env'][env]['AppToken']

    def get_eid_token(self, edge_server, service_id, username, password):
        encrypt_password, rnd = passwordEncryption(password)
        url = f'{edge_server}/auth/v1/service/{service_id}/users/token'
        headers = {'accept': 'application/json', 'content-type': 'application/json;charset=UTF-8'}
        body = {'username': username, 'password': encrypt_password, 'grant_type': 'password', 'challenge': {'type': 'mcpwv3', 'rand': rnd}}
        response = self.s.post(url, headers=headers, json=body)
        eid = response.json()['result']['eid']
        token = response.json()['result']['access_token']

        return eid, token


    def send_notification(self, text):
        edge_server = 'https://hkpd-ed-aws.cx.cinnox.com'
        service_id = self.config['send_notification']['service_id']
        username = self.config['send_notification']['username']
        password = self.config['send_notification']['password']
        room_id_list = self.config['send_notification']['room_id']
        room_name = self.config['send_notification']['room_name']
        eid, token = self.get_eid_token(edge_server, service_id, username, password)

        results = {}
        for room_id in room_id_list:
            url = f'{edge_server}/im/v1/im/events/rooms/{room_id}/message'
            headers = {'x-m800-eid': eid, 'authorization': f'bearer {token}',
                       'x-m800-dp-sendername': 'Monitor',
                       'x-m800-dp-styledtext': 'Monitor',
                       'x-m800-dp-roomname': room_name
                       }
            body = {'type': 1, 'text': f'{text}'}

            response = self.s.post(url, headers=headers, json=body)

            results[room_id] = response.json()

        return results

    def get_recording_file(self, call_id):

        endpoint = f'call-detail?callID={call_id}'
        url = f"{self.Base_URL}/v1/api/apps/{self.appID}/data/{endpoint}"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.AppToken}"
        }

        response = requests.get(url, headers=headers)
        download_url = response.json()['result'][0]['recordingEventList'][0]['files'][0]['downloadUrl']
        logging.info(f'recording download url: {download_url}')

        # 建立不驗證SSL證書的上下文
        ssl_context = ssl._create_unverified_context()

        # 使用urllib.request來下載文件
        with urllib.request.urlopen(download_url, context=ssl_context) as response, open(f'audio_recording/{call_id}.mp4', 'wb') as out_file:
            out_file.write(response.read())

        return download_url

        # wget.download(download_url, out=f'audio_recording/{call_id}.mp3')
# if __name__ == '__main__':
#     ct = CinnoxTool()