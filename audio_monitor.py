import yaml, os
from playwright.sync_api import sync_playwright
from time import sleep
from lib.Logger import Logger
from lib.Browser import Browser
from lib.CinnoxTool import CinnoxTool
from lib.AudioVerification import AudioVerification
from datetime import datetime

def audio_monitor(playwright):
    time_stamp = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
    recording_download_url = ''
    call_id = ''
    test_result = 'FAILED'
    audio_test_result = 'FAILED'
    audfprint_verified_result = decibel_verified_result = False
    step = 'Start testing'
    browser1 = Browser(playwright, lgr, env)
    browser2 = Browser(playwright, lgr, env)
    ct = CinnoxTool(env)


    try:
        step = 'Staff login CXDB site.'
        browser1.go_to(cxdb_url)
        browser1.cinnox_login(account, pwd)
        sleep(5.0)
        step = 'Visitor makes a call.'
        browser2.cxwv_direct_call_enquiry(direct_call_url)
        sleep(5.0)
        step = 'Staff picks up call'
        browser1.cinnox_pickup_call()

        step = 'Staff start call recording.'
        browser1.cinnox_start_recording()

        step = 'Staff end call.'
        browser1.cinnox_end_call()

        step = 'Get call id.'
        call_id = browser1.cinnox_get_call_id()
        sleep(5.0)

        step = 'Close enquiry.'
        browser1.cinnox_close_enquiry()

        step = 'Download recording file.'
        recording_download_url = ct.get_recording_file(call_id)

        step = "Validate the audio's audfprint."
        sp = AudioVerification(call_id, lgr)
        audfprint_verified_result = sp.get_audfprint_verification_result()

        step = "Validate the audio's decibel."
        decibel_verified_result = sp.get_decibel_verification_result()
        test_result = 'SUCCESSFUL'

        if audfprint_verified_result and decibel_verified_result:
            audio_test_result = 'PASSED'

    except Exception as e:
        lgr.error(e)
        assert False
    finally:
        lgr.info('Browsers closed.')
        lgr.info(f'Audio Test Result: {audio_test_result}')
        if test_result == 'FAILED':
            browser1.page.screenshot(path=f'screens/browser1_{time_stamp}.png')
            browser2.page.screenshot(path=f'screens/browser2_{time_stamp}.png')
            text = '=== CXDB Audio Monitor ===\n'
            text += f'Error happened during the step: {step}\n'
            text += 'Please see log file for more details.'
            # text += '........test'
            try:
                ct.send_notification(text)
                lgr.info('Notification is sent to space.')
            except:
                lgr.error('Testing failed, but notification also failed to send.')

        elif test_result == 'SUCCESSFUL':
            if audio_test_result == 'FAILED':
                text = '=== CXDB Audio Monitor ===\n'
                if audfprint_verified_result:
                    text += 'Audfprint Verification Passed'
                else:
                    text += 'Audfprint Verification Failed'
                text += ' & '
                if decibel_verified_result:
                    text += 'Decibel Verification Passed\n'
                else:
                    text += 'Decibel Verification Failed\n'

                text += f'Call ID:{call_id}\n'
                text += f'Recording download url:{recording_download_url}\n'
                try:
                    ct.send_notification(text)
                    lgr.info('Notification is sent to space.')
                except:
                    lgr.error('Audio verification failed, but notification also failed to send.')
            elif audio_test_result == 'PASSED':
                # remove audio recording file
                if os.path.exists(f'audio_recording/{call_id}.mp3'):
                    os.remove(f'audio_recording/{call_id}.mp3')
                    lgr.info('Recording file has been deleted.')
        lgr.info('=' * 20 + '  End running  ' + '=' * 20)
        browser1.close()
        browser2.close()


if __name__ == '__main__':
    # log
    lgr = Logger().logger
    lgr.info('=' * 20 + ' Start running ' + '=' * 20)

    # read config
    config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
    import random
    env = random.choice(list(config['env'].keys()))
    env = 'BJ'
    lgr.info(f'Environment set to [{env}].')
    cxdb_url = config['env'][env]['service']
    account = config['env'][env]['account']
    pwd = config['env'][env]['password']
    direct_call_url = config['env'][env]['direct_call_url']


    with sync_playwright() as playwright:
        audio_monitor(playwright)
