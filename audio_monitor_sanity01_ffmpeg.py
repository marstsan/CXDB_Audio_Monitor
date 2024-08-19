import yaml, os
from playwright.sync_api import sync_playwright
from time import sleep
from lib.Logger import Logger
from lib.Browser import Browser
from lib.CinnoxTool import CinnoxTool
from lib.AudioVerification import AudioVerification
from lib.VideoVerification import VideoVerification
from lib.ffmpeg_recording import ffmpeg_recording
from datetime import datetime, timedelta
import time

def audio_monitor(playwright):
    start_time = time.time()
    is_recording = True
    is_video = True
    verified_video = VideoVerification(lgr)

    test_result = 'FAILED'
    audio_test_result = 'Not yet'
    video_test_result = 'Not yet'
    decibel_test_result = 'Not yet'
    step = 'Start testing'
    browser1 = Browser(playwright, lgr, env, '1')
    browser2 = Browser(playwright, lgr, env, '2')
    browser3 = Browser(playwright, lgr, env, '3')
    browser4 = Browser(playwright, lgr, env, '4')
    ct = CinnoxTool(env)
    ffmpeg_name = 'test_' + (datetime.now().strftime('%Y-%m-%d %H-%M'))
    fr = ffmpeg_recording(lgr, ffmpeg_name)

    try:
        ffmpeg_record = fr.start_screen_recording()
        fr.enable_muti_page()
    except:
        lgr.error('[FFMPEG] Start FFMPEG error')
    # js = js_script()

    try:
        # start playwright traces
        browser1.start_api_traces()
        browser2.start_api_traces()
        browser3.start_api_traces()
        browser4.start_api_traces()

        step = 'StaffA login CXDB site.'

        browser1.go_to(service['service'])

        browser1.cinnox_login(staffA['email'], staffA['password'])

        sleep(5.0)

        step = 'StaffA goes to workspace.'
        workspace_url = service['service'] + '/#/agent-home'
        browser1.go_to(workspace_url)

        step = 'Visitor makes a call to StaffA.'
        browser4.cxwv_direct_call_enquiry(service['direct_call_url'])

        step = 'StaffA picks up call'
        browser1.cinnox_pickup_call()
        sleep(555.0)

        if is_recording:
            filename = '01_visitor'
            step = f"01. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'Mute visitor'
        browser4.cxwv_mute_call()

        step = 'Unmute StaffA'
        browser1.cinnox_mute_call()

        if is_recording:
            filename = '02_staffA'
            step = f"02. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser1.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'StaffB login CXDB site.'
        browser2.go_to(service['service'])
        browser2.cinnox_login(staffB['email'], staffB['password'])
        sleep(10.0)

        step = 'Staff A blind transfer to Staff B'
        browser1.cinnox_bind_transfer(name=staffB['name'])

        step = 'Staff B picks up call'
        browser2.cinnox_pickup_call()
        sleep(2.0)

        step = 'Unmute Visitor'
        browser4.cxwv_mute_call()
        sleep(10.0)

        if is_recording:
            filename = '03_visitor'
            step = f"03. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'Mute Visitor'
        browser4.cxwv_mute_call()

        step = 'Unmute StaffB'
        browser2.cinnox_mute_call()
        sleep(5.0)

        if is_recording:
            filename = '04_staffB'
            step = f"04. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser2.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'StaffC login CXDB site.'
        browser3.go_to(service['service'])
        browser3.cinnox_login(staffC['email'], staffC['password'])
        sleep(10.0)

        step = 'Staff B warm transfer to Staff C'
        browser2.cinnox_warm_transfer(name=staffC['name'])
        sleep(2.0)

        step = 'Staff C picks up call'
        browser3.cinnox_warm_transfer_pickup()
        sleep(5.0)

        if is_recording:
            filename = '05_staffB'
            step = f"05. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser2.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'Mute Staff B'
        browser2.cinnox_mute_call()

        step = 'Unmute Staff C'
        browser3.cinnox_mute_call()
        sleep(5.0)

        if is_recording:
            filename = '06_staffC'
            step = f"06. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser3.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'Staff B confirm warm transfer to Staff C'
        browser2.cinnox_confirm_warm_transfer()
        sleep(10.0)

        if is_recording:
            filename = '07_staffC'
            step = f"07. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser3.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        step = 'Mute Staff C'
        browser3.cinnox_mute_call()

        step = 'Unmute Visitor'
        browser4.cxwv_mute_call()
        sleep(5.0)

        if is_recording:
            filename = '08_Visitor'
            step = f"08. Get {filename}'s .wav file and validate the {filename}'s .wav file."
            sp = AudioVerification(recording_file=filename, lgr=lgr)
            verified_sound = sp.get_audfprint_verification_result()
            if not verified_sound:
                audio_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate the audio_recording/{filename}'s .wav failed")

        audio_test_result = 'PASSED'

        step = 'Unmute Staff C'
        browser3.cinnox_mute_call()
        sleep(3.0)

        step = 'Staff C starts call recording'
        browser3.cinnox_start_recording()

        step = 'Stacc C scale up call view'
        browser3.cinnox_scale_up()
        sleep(3.0)

        step = 'Staff C starts camera'
        browser3.cinnox_start_camera()
        sleep(5)

        step = 'Visitor starts camera'
        browser4.cinnox_start_camera()
        sleep(5)

        step = '01. Browser3 takes a screenshot'
        browser3.page.screenshot(path=f'video_screenshot/camera/01_1on1_visitor.png')
        sleep(2)

        if is_video:
            step = '01. Validate 01_1on1_visitor.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/01_1on1_visitor.png', 'visitor')
            if not verified_result:
                video_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffC 看不到 Visitor 的 camera 或 StaffC 看不到自己的 camera)")

        step = '02. Browser4 takes a screenshot'
        browser4.page.screenshot(path=f'video_screenshot/camera/02_1on1_staffC.png')
        sleep(2)

        # verified_video = VV.get_predict_result('video_screenshot/camera/2_1on1_staffC.png', 'staffC', lgr)
        if is_video:
            step = '02. Validate 02_1on1_staffC.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/02_1on1_staffC.png', 'staffC')
            if not verified_result:
                video_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到 StaffC 的 camera 或 Visitor 看不到自己的 camera)")

        step = 'Staff C starts screen sharing'
        browser3.cinnox_start_screen_sharing()
        sleep(5)

        step = 'Visitor starts screen sharing'
        browser4.cinnox_start_screen_sharing()
        sleep(5)

        step = '03. Browser3 takes a screenshot'
        browser3.page.screenshot(path=f'video_screenshot/screensharing/03_1on1_visitor.png')
        sleep(2)

        # verified_video = VV.get_predict_result('video_screenshot/screensharing/3_1on1_visitor.png', 'sharescreen', lgr)
        if is_video:
            step = '03. Validate 03_1on1_visitor.png (screen sharing)'
            verified_result = verified_video.get_predict_result('video_screenshot/screensharing/03_1on1_visitor.png', 'sharescreen')
            if not verified_result:
                video_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffC 看不到 Visitor 的 screen share 或 StaffC 看不到自己的 screen share)")
                # raise Exception(f"Validate the screen sharing failed")

        step = '04. Browser4 takes a screenshot'
        browser4.page.screenshot(path=f'video_screenshot/screensharing/04_1on1_staffC.png')
        sleep(2)

        # verified_video = VV.get_predict_result('video_screenshot/screensharing/4_1on1_staffC.png', 'sharescreen', lgr)
        if is_video:
            step = '04. Validate 04_1on1_staffC.png (screen sharing)'
            verified_result = verified_video.get_predict_result('video_screenshot/screensharing/04_1on1_staffC.png', 'sharescreen')
            if not verified_result:
                video_test_result = 'FAILED'
                browser4.cinnox_end_call()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到 StaffC 的 screen share 或 Visitor 看不到自己的 screen share)")
                # raise Exception(f"Validate the screen sharing failed")

        step = 'Visitor stop screen sharing'
        browser4.cinnox_start_screen_sharing()
        sleep(5.0)

        step = 'Staff C starts conference call'
        browser3.cinnox_start_1on1_conference(staffA['name'])
        sleep(2.0)

        step = 'Staff A accept the conference'
        browser1.cinnox_accept_conference()
        sleep(5.0)

        step = 'Staff A scale up call view'
        browser1.cinnox_scale_up()
        sleep(3.0)

        step = 'Staff A turn off camera'
        browser1.cinnox_start_camera()
        sleep(2.0)

        step = 'Staff C starts camera'
        browser3.cinnox_start_conference_camera()
        sleep(10.0)

        step = 'Staff A switch to Staff C card'
        browser1.cinnox_switch_conference_card(staffC['name'])

        step = 'Visitor switch to Staff C card'
        browser4.cinnox_switch_conference_card(staffC['name'])

        step = 'Staff C switch to Staff C card'
        browser3.cinnox_switch_conference_card(staffC['name'])
        sleep(5.0)

        step = '05. Browser1 takes a conference screenshot'
        browser1.page.screenshot(path=f'video_screenshot/camera/05_browser1_conference_staffC.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/5_browser1_conference_staffC.png', 'staffC', lgr)
        if is_video:
            step = '05. Validate 05_browser1_conference_staffC.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/05_browser1_conference_staffC.png', 'staffC')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffA 看不到 StaffC 的 camera)")

        step = '06. Browser3 takes a conference screenshot'
        browser3.page.screenshot(path=f'video_screenshot/camera/06_browser3_conference_staffC.png')
        sleep(2.0)
        # verified_video = VV.get_predict_result('video_screenshot/camera/6_browser3_conference_staffC.png', 'staffC', lgr)
        if is_video:
            step = '06. Validate 06_browser3_conference_staffC.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/06_browser3_conference_staffC.png', 'staffC')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffC 看不到自己的 camera)")

        step = '07. Browser4 takes a conference screenshot'
        browser4.page.screenshot(path=f'video_screenshot/camera/07_browser4_conference_staffC.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/7_browser4_conference_staffC.png', 'staffC', lgr)
        if is_video:
            step = '07. Validate 07_browser4_conference_staffC.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/07_browser4_conference_staffC.png', 'staffC')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到 StaffC 的 camera)")

        # step = 'Staff A starts camera'
        # browser1.cinnox_start_conference_camera()
        # sleep(10.0)
        step = 'Staff A turn on camera'
        browser1.cinnox_start_camera()
        sleep(3.0)

        step = 'Staff A switch to Staff A card'
        browser1.cinnox_switch_conference_card(staffA['name'])

        step = 'Visitor switch to Staff A card'
        browser4.cinnox_switch_conference_card(staffA['name'])

        step = 'Staff C switch to Staff A card'
        browser3.cinnox_switch_conference_card(staffA['name'])
        sleep(5.0)

        step = '08. Browser1 takes a conference screenshot'
        browser1.page.screenshot(path=f'video_screenshot/camera/08_browser1_conference_staffA.png')
        sleep(2.0)
        # verified_video = VV.get_predict_result('video_screenshot/camera/8_browser1_conference_staffA.png', 'staffA', lgr)
        if is_video:
            step = '08. Validate 08_browser1_conference_staffA.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/08_browser1_conference_staffA.png', 'staffA')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffA 看不到自己的 camera)")

        step = '09. Browser3 takes a conference screenshot'
        browser3.page.screenshot(path=f'video_screenshot/camera/09_browser3_conference_staffA.png')
        sleep(2.0)
        # verified_video = VV.get_predict_result('video_screenshot/camera/9_browser3_conference_staffA.png', 'staffA', lgr)
        if is_video:
            step = '09. Validate 09_browser3_conference_staffA.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/09_browser3_conference_staffA.png', 'staffA')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffC 看不到 StaffA 的 camera)")

        step = '10. Browser4 takes a conference screenshot (camera)'
        browser4.page.screenshot(path=f'video_screenshot/camera/10_browser4_conference_staffA.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/10_browser4_conference_staffA.png', 'staffA', lgr)
        if is_video:
            step = '10. Validate 10_browser4_conference_staffA.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/10_browser4_conference_staffA.png', 'staffA')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到 StaffA 的 camera)")

        # step = 'Visitor stop screen sharing'
        # browser4.cinnox_start_screen_sharing()
        # sleep(5.0)

        step = 'Visitor starts camera'
        browser4.cinnox_start_conference_camera()
        sleep(10.0)

        step = 'Staff A switch to Visitor card'
        visitor_name = 'TW-webDesktop-158'
        browser1.cinnox_switch_conference_card(visitor_name)

        step = 'Visitor switch to Visitor card'
        browser4.cinnox_switch_conference_card(visitor_name)

        step = 'Staff C switch to Visitor card'
        browser3.cinnox_switch_conference_card(visitor_name)
        sleep(5.0)

        step = '11. Browser1 takes a conference screenshot'
        browser1.page.screenshot(path=f'video_screenshot/camera/11_browser1_conference_visitor.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/11_browser1_conference_visitor.png', 'visitor', lgr)
        if is_video:
            step = '11. Validate 11_browser1_conference_visitor.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/11_browser1_conference_visitor.png', 'visitor')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffA 看不到 Visitor 的 camera)")

        step = '12. Browser3 takes a conference screenshot'
        browser3.page.screenshot(path=f'video_screenshot/camera/12_browser3_conference_visitor.png')
        sleep(2.0)
        # verified_video = VV.get_predict_result('video_screenshot/camera/12_browser3_conference_visitor.png', 'visitor', lgr)
        if is_video:
            step = '12. Validate 12_browser3_conference_visitor.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/12_browser3_conference_visitor.png', 'visitor')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffC 看不到 Visitor 的 camera)")

        step = '13. Browser4 takes a conference screenshot'
        browser4.page.screenshot(path=f'video_screenshot/camera/13_browser4_conference_visitor.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/13_browser4_conference_visitor.png', 'visitor', lgr)
        if is_video:
            step = '13. Validate 13_browser4_conference_visitor.png (camera)'
            verified_result = verified_video.get_predict_result('video_screenshot/camera/13_browser4_conference_visitor.png', 'visitor')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到自己的 camera)")

        step = 'Staff C starts screen sharing'
        browser3.cinnox_start_screen_sharing()
        sleep(10)

        step = '14. Browser1 takes a conference screenshot'
        browser1.page.screenshot(path=f'video_screenshot/screensharing/14_browser1_conference_staffC.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/14_browser1_conference_staffC.png', 'sharescreen', lgr)
        if is_video:
            step = '14. Validate 14_browser1_conference_staffC.png (screen sharing)'
            verified_result = verified_video.get_predict_result('video_screenshot/screensharing/14_browser1_conference_staffC.png', 'sharescreen')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (StaffA 看不到 StaffC 的 screen share)")

        # step = 'Browser3 takes a conference screenshot'
        # time_stamp = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H-%M-%SZ')
        # browser3.page.screenshot(path=f'video_screenshot/screensharing/browser3_camera_{time_stamp}.png')

        step = '15. Browser4 takes a conference screenshot'
        browser4.page.screenshot(path=f'video_screenshot/screensharing/15_browser4_conference_staffC.png')
        sleep(2.0)

        # verified_video = VV.get_predict_result('video_screenshot/camera/15_browser4_conference_staffC.png', 'sharescreen', lgr)
        if is_video:
            step = '15. Validate 15_browser4_conference_staffC.png (screen sharing)'
            verified_result = verified_video.get_predict_result('video_screenshot/screensharing/15_browser4_conference_staffC.png', 'sharescreen')
            if not verified_result:
                video_test_result = 'FAILED'
                browser3.cinnox_end_conference()
                raise Exception(f"Validate {step.split('Validate')[1].strip()} failed. (Visitor 看不到 StaffC 的 screen share)")

        video_test_result = 'PASSED'

        step = 'Staff C end conference'
        browser3.cinnox_end_conference()

        step = 'Browser4 go to workspace'
        workspace_url = service['service'] + '/#/agent-home'
        browser3.go_to(workspace_url)
        sleep(5.0)

        step = 'Get call id.'
        call_id = browser3.cinnox_get_call_id()

        step = 'Close enquiry.'
        browser3.cinnox_close_enquiry()

        step = 'Download recording file.'
        recording_download_url = ct.get_recording_file(call_id)

        step = "Validate the recording's decibel."
        check_db = AudioVerification(call_id=call_id, lgr=lgr)
        decibel_verified_result = check_db.get_decibel_verification_result()
        if not decibel_verified_result:
            decibel_test_result = 'FAILED'
            raise Exception(f"Validate the decibel failed")

        decibel_test_result = 'PASSED'
        test_result = 'SUCCESSFUL'

    except Exception as e:
        lgr.error(e)
        time_stamp = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H-%M-%SZ')
        browser1.stop_api_traces(file_name=f'browser1/{time_stamp}')
        browser2.stop_api_traces(file_name=f'browser2/{time_stamp}')
        browser3.stop_api_traces(file_name=f'browser3/{time_stamp}')
        browser4.stop_api_traces(file_name=f'browser4/{time_stamp}')
        assert False
    finally:
        try:
            ffmpeg_record.terminate()
            fr.disable_muti_page()
        except:
            lgr.error('[FFMPEG] Stop FFMPEG error')

        lgr.info(f'Audio Test Result: {audio_test_result}')
        lgr.info(f'Video Test Result: {video_test_result}')
        lgr.info(f'Decibel Test Result: {decibel_test_result}')
        if test_result == 'FAILED':
            time_stamp = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H-%M-%SZ')
            browser1.page.screenshot(path=f'screens/browser1_{time_stamp}.png')
            browser2.page.screenshot(path=f'screens/browser2_{time_stamp}.png')
            browser3.page.screenshot(path=f'screens/browser3_{time_stamp}.png')
            browser4.page.screenshot(path=f'screens/browser4_{time_stamp}.png')
            text = '=== CXDB Audio/Video Monitor ===\n'
            text += f'Environment set to [{env}].\n'
            text += f'Error happened during the step: {step}\n'
            text += 'Please see log file for more details. (http://172.31.32.58:8081/log)\n'
            if audio_test_result == 'FAILED':
                text += 'Please see Audio tab from streamlit APP (http://172.31.32.58:8504)\n'
                text += 'http://172.31.32.58:8081/audio_recording/error'

            elif video_test_result == 'FAILED':
                text += 'Please see Video tab from streamlit APP (http://172.31.32.58:8504)\n'
                text += 'http://172.31.32.58:8081/video_screenshot/error'
            elif decibel_test_result == 'FAILED':
                text += 'Please see Recording tab from streamlit APP (http://172.31.32.58:8504)\n'
                text += 'http://172.31.32.58:8081/audio_recording'

            try:
                ct.send_notification(text)
                lgr.info('Notification is sent to space.')
            except:
                lgr.error('Testing failed, but notification also failed to send.')

        else:
            try:
                fr.rmove_recording_file()
            except:
                lgr.error('[FFMPEG] Remove ffmepg file error')

        browser1.close()
        browser2.close()
        browser3.close()
        browser4.close()
        lgr.info('Browsers closed.')
        elapsed_time = time.time() - start_time
        lgr.info(f"程式碼執行時間：{elapsed_time} 秒")
        lgr.info('=' * 20 + '  End running  ' + '=' * 20)

if __name__ == '__main__':
    import sys, random

    if len(sys.argv) < 2:
        print('please give argument for region: HK/SG/JP/BJ.')
        sys.exit()
    region = sys.argv[1]

    if region == 'random':
        regionlist = ['SG', 'JP', 'HK', 'BJ']
        env = random.choice(regionlist)
    else:
        env = region

    # log
    lgr = Logger().logger
    lgr.info('=' * 20 + ' Start running ' + '=' * 20)
    # read config
    config = yaml.load(open('account_config.yaml'), Loader=yaml.FullLoader)

    lgr.info(f'Environment set to [{env}].')

    service, staffA, staffB, staffC = (config[env], config[env]['account']['staffA'], config[env]['account']['staffB'], config[env]['account']['staffC'])

    with sync_playwright() as playwright:
        audio_monitor(playwright)
