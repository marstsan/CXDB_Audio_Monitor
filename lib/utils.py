from pathlib import Path
import json
import requests
from lib.loginEncrypt import passwordEncryption
from random import getrandbits
import os
import logging
import base64
import random



class TestUtil:



    @staticmethod
    def clean_test_env(serviceId: str, username: str, password: str, stage: str):
        # Get token and eid
        if stage == 'testbed' or stage == 'TESTBED':
            edgeServer = 'hktb-ed.cx-tb.cinnox.com'
        elif stage == 'testbed01' or stage == 'TESTBED01':
            edgeServer = 'hktb-ed.cx-tb1.cinnox.com'
        elif stage == 'int' or stage == 'INT':
            edgeServer = 'edge-int.m800.com'
        elif stage == 'prod' or stage == 'PROD':
            edgeServer = 'hkpd-ed-aws.cx.cinnox.com'
        elif stage == 'prp' or stage == 'PRP':
            edgeServer = 'hkprp-ed.cx-prp.cinnox.com'
        elif stage == 'loadtest' or stage == 'loadtest':
            edgeServer = 'hklt-ed.mc-lt.maaiiconnect.com'
        else:
            print('Wrong stage, check your setting, e.g. testbed, prod')
            exit()

        encrypted_passwd, rnd = passwordEncryption(password)
        url = 'https://' + edgeServer + '/auth/v1/service/' + serviceId + '/users/token'
        header = {"Content-type": "application/json"}
        payload = {
            "username": username,
            "password": encrypted_passwd,
            "grant_type": "password",
            "challenge": {
                "type": "mcpwv3",
                "rand": rnd
            }
        }

        try:
            res = requests.post(url, headers=header, data=json.dumps(payload))
            access_token = 'bearer ' + (res.json())['result']['access_token']
            eid = (res.json())['result']['eid']

            # Get devices
            url = 'https://' + edgeServer + '/lc-ds/v1/services/' + serviceId + '/license/' + eid
            header = {"authorization": access_token, "x-m800-eid": eid}
            res = requests.get(url, headers=header)
            deviceList = []

            if 'web' in (res.json())['result']['deviceList'].keys():
                for device in (res.json())['result']['deviceList']['web']:
                    deviceList.append(device)

            if 'mobile' in (res.json())['result']['deviceList'].keys():
                for device in (res.json())['result']['deviceList']['mobile']:
                    deviceList.append(device)

            # Logout all devices
            url = 'https://' + edgeServer + '/lc-ds/v1/services/' + serviceId + '/staff/' + eid + '/devices'
            header = {"authorization": access_token, "x-m800-eid": eid}
            payload = {"deviceList": deviceList}

            requests.delete(url, headers=header, data=json.dumps(payload))

            # Delete all visitor inquiries
            url = 'https://' + edgeServer + '/lc-orc/v1/services/' + serviceId + "/users/" + eid + "/conversations"
            header = {"authorization": access_token, "x-m800-eid": eid}
            params = {'histories': 'false', 'cursor': 'false', 'limit': 200}
            res = requests.get(url, headers=header, params=params)

            url = 'https://' + edgeServer + '/lc-orc/v1/services/' + serviceId + "/inquiries/"
            header = {"authorization": access_token, "x-m800-eid": eid}

            for conversation in (res.json())['result']:
                if conversation['type'] == 1001:
                    inquiryId = conversation['inquiry']['id']
                    requests.delete(url + inquiryId, headers=header)
        except:
            pass

    @staticmethod
    def close_all_enquiries(serviceId: str, username: str, password: str, stage: str):
        # Get token and eid
        if stage == 'testbed' or stage == 'TESTBED':
            edgeServer = 'hktb-ed.cx-tb.cinnox.com'
        elif stage == 'testbed01' or stage == 'TESTBED01':
            edgeServer = 'hktb-ed.cx-tb1.cinnox.com'
        elif stage == 'int' or stage == 'INT':
            edgeServer = 'edge-int.m800.com'
        elif stage == 'prod' or stage == 'PROD':
            edgeServer = 'hkpd-ed-aws.cx.cinnox.com'
        elif stage == 'prp' or stage == 'PRP':
            edgeServer = 'hkprp-ed.cx-prp.cinnox.com'
        elif stage == 'loadtest' or stage == 'loadtest':
            edgeServer = 'hklt-ed.mc-lt.maaiiconnect.com'
        else:
            print('Wrong stage, check your setting, e.g. testbed, prod')
            exit()

        encrypted_passwd, rnd = passwordEncryption(password)
        url = 'https://' + edgeServer + '/auth/v1/service/' + serviceId + '/users/token'
        header = {"Content-type": "application/json"}
        payload = {
            "username": username,
            "password": encrypted_passwd,
            "grant_type": "password",
            "challenge": {
                "type": "mcpwv3",
                "rand": rnd
            }
        }

        try:
            res = requests.post(url, headers=header, data=json.dumps(payload))
            access_token = 'bearer ' + (res.json())['result']['access_token']
            eid = (res.json())['result']['eid']

            # Delete all visitor inquiries
            url = 'https://' + edgeServer + '/lc-orc/v1/services/' + serviceId + "/users/" + eid + "/conversations"
            header = {"authorization": access_token, "x-m800-eid": eid}
            params = {'histories': 'false', 'cursor': 'false', 'limit': 200}
            res = requests.get(url, headers=header, params=params)

            url = 'https://' + edgeServer + '/lc-orc/v1/services/' + serviceId + "/inquiries/"
            header = {"authorization": access_token, "x-m800-eid": eid}

            for conversation in (res.json())['result']:
                if conversation['type'] == 1001:
                    inquiryId = conversation['inquiry']['id']
                    requests.delete(url + inquiryId, headers=header)
        except:
            pass

    @staticmethod
    def make_tf_call_using_e2e_tool(caller_number: str):
        # Offnet call E2E test tool was built by call team, but right now need to be pre-provisioned
        # Right now, only numbers in tb-hk-02 was supported in order not to increase the complexity of func

        transcoder_ip = '207.226.217.85'
        destination_number = "0017170809093201"

        url = f'http://{transcoder_ip}:8080/tf_in'
        header = {"Content-type": "application/json"}
        payload = {
            "caller_number": caller_number,
            "destination_numer": destination_number
        }

        response = requests.post(url, headers=header, data=json.dumps(payload))

        return response.status_code

    @staticmethod
    def get_test_status(run_id, case_id):
        base_URL = 'https://192.168.118.152/index.php?/api/v2/'
        testrail_account = 'rickchen@m800.com'
        testrail_password = 'Zcadqe!3'
        headers = {"Content-Type": "application/json"}
        s = requests.Session()

        get_run_status = s.get(base_URL + 'get_tests/' + run_id, headers=headers, verify=False, auth=(testrail_account, testrail_password))

        for run in get_run_status.json():
            if run['case_id'] == int(case_id):
                return run['status_id']

    def start_enquiry_3rd_party(baseURL, token):
        url = f'{baseURL}/lc-orc/v1/omni-channels/hooks/thirdparty'
        headers = {'Content-Type': 'application/json'}
        data = {
            "userInfo": {
                "language": "zh-tw",
                "nickname": "Test third party enquiry",
                "userId": "Automation Testing",
                "avatarUrl": "https://aaa.aaaa"
            },
            "accessToken": token,
            "message": {
                "type": 2,
                "text": "Automation Testing",
                "file": [
                    {
                        "mimeType": "image/jpeg",
                        "size": 19073,
                        "type": 1,
                        "downloadUrl": "https://stickershop.line-scdn.net/stickershop/v1/product/1233739/LINEStorePC/main.png",
                        "name": "main.png"
                    }
                ]
            }
        }
        s = requests.Session()
        response = s.post(url, data=json.dumps(data), headers=headers, timeout=30)

        return response.json()

    @staticmethod
    def write_status_as_other_case(run_id, case_id):
        try:
            status = TestUtil.get_test_status(run_id, case_id)
            if status == 1:
                pass
            elif status == 5:
                assert False
        except:  # exception if run ID is incorrectly, or cannot get pass/failed status
            assert False

    @staticmethod
    def make_third_party_enquiry(stage: str, token: str, message: str):
        # Get token and eid
        if stage == 'testbed' or stage == 'TESTBED':
            edgeServer = 'hktb-ed.cx-tb.cinnox.com'
        elif stage == 'testbed01' or stage == 'TESTBED01':
            edgeServer = 'hktb-ed.cx-tb1.cinnox.com'
        elif stage == 'int' or stage == 'INT':
            edgeServer = 'edge-int.m800.com'
        elif stage == 'prod' or stage == 'PROD':
            edgeServer = 'hkpd-ed-aws.cx.cinnox.com'
        elif stage == 'prp' or stage == 'PRP':
            edgeServer = 'hkprp-ed.cx-prp.cinnox.com'
        elif stage == 'loadtest' or stage == 'loadtest':
            edgeServer = 'hklt-ed.mc-lt.maaiiconnect.com'
        else:
            print('Wrong stage, check your setting, e.g. testbed, prod')
            exit()

        url = f'https://{edgeServer}/lc-orc/v1/omni-channels/hooks/thirdparty'
        header = {"Content-type": "application/json"}
        payload = {
            "userInfo": {
                "language": "zh-tw",
                "nickname": "3rd_party_user",
                "userId": "3rd_party_user",
                "avatarUrl": "https://imgur.com/gallery/sKH3HfP"
            },
            "accessToken": token,
            "message": {
                "type": 2,
                "text": message,
                "file": [
                    {
                        "mimeType": "image/jpeg",
                        "size": 19073,
                        "type": 1,
                        "downloadUrl": "https://stickershop.line-scdn.net/stickershop/v1/product/1233739/LINEStorePC/main.png",
                        "name": "main.png"
                    }
                ]
            }
        }

        requests.post(url, headers=header, data=json.dumps(payload))

    @staticmethod
    def setup_staff_limit(env: str, serviceID: str, staffNumber: int):
        if env == 'tb1':
            url = 'http://172.30.100.200:30731/internal/v1/services/' + serviceID + '/billing'
        elif env == 'tb2':
            url = 'http://172.30.100.200:30631/internal/v1/services/' + serviceID + '/billing'

        headers = {'Content-Type': 'application/json', 'X-m800-svc': 'provision.m800.com'}
        data = {"chargingFeatureSetting": {"staffLimit": staffNumber}}

        requests.put(url, data=json.dumps(data), headers=headers, timeout=30)

    @staticmethod
    def get_storage_detail(serviceId: str, username: str, password: str, stage: str):
        # Get token and eid
        if stage == 'testbed' or stage == 'TESTBED':
            edgeServer = 'hktb-ed.cx-tb.cinnox.com'
        elif stage == 'testbed01' or stage == 'TESTBED01':
            edgeServer = 'hktb-ed.cx-tb1.cinnox.com'
        elif stage == 'int' or stage == 'INT':
            edgeServer = 'edge-int.m800.com'
        elif stage == 'prod' or stage == 'PROD':
            edgeServer = 'hkpd-ed-aws.cx.cinnox.com'
        elif stage == 'prp' or stage == 'PRP':
            edgeServer = 'hkprp-ed.cx-prp.cinnox.com'
        elif stage == 'loadtest' or stage == 'loadtest':
            edgeServer = 'hklt-ed.cx-lt.cinnox.com'
        else:
            print('Wrong stage, check your setting, e.g. testbed, prod')
            exit()

        encrypted_passwd, rnd = passwordEncryption(password)
        url = 'https://' + edgeServer + '/auth/v1/service/' + serviceId + '/users/token'
        header = {"Content-type": "application/json"}
        payload = {
            "username": username,
            "password": encrypted_passwd,
            "grant_type": "password",
            "challenge": {
                "type": "mcpwv3",
                "rand": rnd
            }
        }

        s = requests.Session()
        res = requests.post(url, headers=header, data=json.dumps(payload))
        access_token = 'bearer ' + (res.json())['result']['access_token']
        eid = (res.json())['result']['eid']

        # Request Storage Details
        url = f'https://{edgeServer}/file-management/v1/usage'
        headers = {'x-m800-eid': eid, 'authorization': f'{access_token}'}
        response = s.get(url, headers=headers)
        imStorage = response.json()['result']['usageStatistics']['imStorage']

        return imStorage

    @staticmethod
    def android_start_screen_recording(driver):  # folderName, fileName
        logging.info('Start Screen Recording...')
        driver.start_recording_screen()
        # command = f"adb shell screenrecord /sdcard/Android_Automation_Recording/{folderName}/{fileName}.mp4"
        # return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def android_stop_screen_recording(driver, fileName: str):
        logging.info('Stop Screen Recording')
        # process.send_signal(signal.SIGINT)
        video_rawdata = driver.stop_recording_screen()
        file_path = pytest.root_folder + '/AndroidScreenRecord'
        filepath = os.path.join(file_path, fileName + ".mp4")
        with open(filepath, "wb") as vd:
            vd.write(base64.b64decode(video_rawdata))

    @staticmethod
    def ios_start_screen_recording(driver):
        logging.info('Start Screen Recording...')
        args = dict(
            forceRestart=True,
            timeLimit=60 * 10,
            videoType='h264',
            videoFps=24,
            videoScale="320:-2"
        )
        driver.start_recording_screen(**args)

    @staticmethod
    def ios_stop_screen_recording(driver, fileName: str):
        logging.info('Stop Screen Recording')
        video_rawdata = driver.stop_recording_screen()
        file_path = pytest.root_folder + '/iOSScreenRecord'
        filepath = os.path.join(file_path, fileName + ".mp4")
        with open(filepath, "wb") as vd:
            vd.write(base64.b64decode(video_rawdata))

    @staticmethod
    def start_IM_chat_enquiry(serviceId: str, targetId: str, stage: str, destType: str):
        # Get token and eid
        if stage == 'testbed' or stage == 'TESTBED':
            edgeServer = 'hktb-ed.cx-tb.cinnox.com'
        elif stage == 'testbed01' or stage == 'TESTBED01':
            edgeServer = 'hktb-ed.cx-tb1.cinnox.com'
        elif stage == 'int' or stage == 'INT':
            edgeServer = 'edge-int.m800.com'
        elif stage == 'prod' or stage == 'PROD':
            edgeServer = 'hkpd-ed-aws.cx.cinnox.com'
        elif stage == 'prp' or stage == 'PRP':
            edgeServer = 'hkprp-ed.cx-prp.cinnox.com'
        elif stage == 'loadtest' or stage == 'loadtest':
            edgeServer = 'hklt-ed.mc-lt.maaiiconnect.com'
        else:
            print('Wrong stage, check your setting, e.g. testbed, prod')
            exit()
        s = requests.Session()
        endpoint = f'/auth/v2/service/{serviceId}/users/anonymous/onestep'
        url = 'https://' + edgeServer

        choice = 'abcdef0123456789'
        device_id = ''
        device_id = device_id + ''.join(random.choice(choice) for _ in range(0, 8)) + '-' + \
                    ''.join(random.choice(choice) for _ in range(0, 4)) + '-' + \
                    ''.join(random.choice(choice) for _ in range(0, 4)) + '-' + \
                    ''.join(random.choice(choice) for _ in range(0, 4)) + '-' + \
                    ''.join(random.choice(choice) for _ in range(0, 12))
        try:
            url = url + endpoint
            headers = {'content-type': 'application/json;charset=UTF-8'}
            # Get eid and token
            response = s.post(url, headers=headers)

            data = response.json()['result']
            eid = data['eid']
            token = data['access_token']

            inquiry_url = 'https://' + edgeServer + '/lc-orc/v1/services/' + serviceId + '/conversation-operations/inquiry'
            headers = {'content-type': 'application/json;charset=UTF-8',
                       'authorization': f'bearer {token}',
                       'x-m800-eid': eid,
                       'x-m800-deviceid': device_id,
                       'x-m800-platform': 'web'
                       }
            if destType == 'staff':
                inquiry_data = {'channel': 'IM', 'staff': targetId}
            elif destType == 'tagID':
                inquiry_data = {'channel': 'IM', 'tagID': targetId}
            else:
                print('Wrong destType, check your setting, e.g. tagID, staff')
                exit()
            # Send IM enquiry
            s.post(inquiry_url, headers=headers, json=inquiry_data)
        except:
            pass

    @staticmethod
    def generate_device_id():
        gen_str = '%032x' % getrandbits(128)
        device_id = f'{gen_str[:8]}-{gen_str[8:12]}-{gen_str[12:16]}-{gen_str[16:20]}-{gen_str[20:]}'
        return device_id