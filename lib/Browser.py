import pyperclip
from playwright.sync_api import sync_playwright
from time import sleep, time
import sys, os


class Browser:
    def __init__(self, playwright: sync_playwright, lgr, env, browser: str):
        self.lgr = lgr
        self.env = env
        size = {'width': 1280, 'height': 700}
        if sys.platform == 'win32':
            path_prefix = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/'
        else:
            path_prefix = ''

        self.browserArgs1 = [
            '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream',
            '--no-sandbox',
            '--disable-gpu',
            '--window-position=0,0',
            '--allow-file-access-from-files',
            '--disable-gesture-requirement-for-media-playback',
            f'--use-file-for-fake-audio-capture={path_prefix}audio_sample/StaffA_soundEN.wav',
            f'--use-file-for-fake-video-capture={path_prefix}video_sample/video1.mjpeg']

        self.browserArgs2 = [
            '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream',
            '--no-sandbox',
            '--disable-gpu',
            '--disable-extensions',
            '--window-position=10,800',
            f'--use-file-for-fake-audio-capture={path_prefix}audio_sample/StaffB_soundEN.wav',
            f'--use-file-for-fake-video-capture={path_prefix}video_sample/video2.mjpeg']

        self.browserArgs3 = [
            '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream',
            '--no-sandbox',
            '--disable-gpu',
            '--disable-extensions=10,800',
            f'--use-file-for-fake-audio-capture={path_prefix}audio_sample/StaffC_soundEN.wav',
            f'--use-file-for-fake-video-capture={path_prefix}video_sample/video3.mjpeg']

        self.browserArgs4 = [
            '--use-fake-device-for-media-stream',
            '--use-fake-ui-for-media-stream',
            '--no-sandbox',
            '--disable-gpu',
            '--disable-extensions',
            '--window-position=30,800',
            f'--use-file-for-fake-audio-capture={path_prefix}audio_sample/enquiry_sound.wav',
            f'--use-file-for-fake-video-capture={path_prefix}video_sample/video4.mjpeg']

        if browser == '1':
            self.browser = playwright.chromium.launch(headless=False, args=self.browserArgs1, channel='chrome')
        elif browser == '2':
            self.browser = playwright.chromium.launch(headless=False, args=self.browserArgs2, channel='chrome')
        elif browser == '3':
            self.browser = playwright.chromium.launch(headless=False, args=self.browserArgs3, channel='chrome')
        elif browser == '4':
            self.browser = playwright.chromium.launch(headless=False, args=self.browserArgs4, channel='chrome')

        self.context = self.browser.new_context(viewport=size)
        self.page = self.context.new_page()
        # lgr.info('Browser initialize complete.')

    def start_api_traces(self):
        self.context.tracing.start(screenshots=False, snapshots=True)

    def stop_api_traces(self, file_name):

        self.context.tracing.stop(path=f"api_traces/{file_name}.zip")

    def go_to(self, url):
        self.page.goto(url)
        # self.lgr.info(f'Launch to url: {url}')

    def close(self):
        self.browser.close()

    # def get_audio_data(self, js_script, fileName):
    #     audio_data_base64 = self.page.evaluate(js_script)
    #     audio_data = base64.b64decode(audio_data_base64)
    #     audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
    #     audio.export(f"audio_recording/{fileName}.mp3", format="mp3")

    def get_download_url(self):
        audio_url = self.page.evaluate('window.audioUrl')
        return audio_url

    # ----- Cinnox functions -----
    def cinnox_login(self, username, password):
        start_time = time()
        self.page.locator('[data-testid="email"]').fill(username)
        self.lgr.info(f'[Cinnox] Fill in email')
        self.page.fill('[data-testid="password"]', password)
        self.lgr.info(f'[Cinnox] Fill in password')
        self.page.click('[data-testid="login-button"]')
        self.lgr.info(f'[Cinnox] Click on login button')
        # self.page.wait_for_selector('[data-testid="get-started-menu-welcome"]', timeout=60000)
        # self.page.wait_for_load_state('networkidle')
        end_time = time()
        load_time = round(end_time - start_time, 3)
        self.lgr.info(f'[Cinnox] Login Cinnox service spent {load_time} seconds')

    def cinnox_pickup_call(self):
        self.lgr.info('[Cinnox] Staff pick up call')
        # self.page.click('[data-testid="enquiry-centre-btn"]')
        sleep(1.5)
        # self.page.click('[data-testid="enquiry-centre-panel-pending-inquiry-directCallInquiry"]')
        self.page.click('[data-testid="call-answer"]')
        self.lgr.info('[Cinnox] Staff mute the call')
        self.page.click('[data-testid="call-mute"]')

    def cinnox_warm_transfer_pickup(self):
        self.page.click('[data-testid="call-answer"]')
        self.page.click('[data-testid="call-mute"]')

    def cinnox_mute_call(self):
        self.page.click('[data-testid="call-mute"]')

    def cinnox_start_recording(self):
        self.page.click('[data-testid="call-record"]')
        sleep(10)

    def cinnox_end_call(self):
        self.page.click('[data-testid="call-end"]')

    def cinnox_start_camera(self):
        # self.page.click('[data-testid="call-more"]')
        self.page.click('[data-testid="call-camera"]')

    def cinnox_start_conference_camera(self):
        self.page.click('[data-testid="call-camera"]')

    def cinnox_start_screen_sharing(self):
        self.page.click('[data-testid="call-shareScreen"]')

    def cinnox_end_conference(self):
        self.page.click('[data-testid="call-end"]')
        self.page.click('[data-testid="terminate-conference"]')
        sleep(5.0)

    def cinnox_start_1on1_conference(self, name):
        # self.page.click('[data-testid="call-scaleUp"]')
        self.page.click('[data-testid="invite-participant"]')
        self.page.fill('[data-testid="search-conference-staff-list"]', name)
        sleep(2.0)
        self.page.click('//button[@data-testid="add-staff"][1]')
        sleep(1.0)

    def cinnox_switch_conference_card(self, name):
        self.page.click(f'//*[@data-testid="join-member-webcam"]//span[text()="{name}"]')
        # self.page.click(f'//*[@data-testid="join-member-webcam"]/*/div[text()="{name}"]')
        # self.page.click(f'xpath=//div[text()="{name}"]')

    def cinnox_scale_up(self):
        self.page.click('[data-testid="call-scaleUp"]')

    def cinnox_accept_conference(self):
        self.page.click('[data-testid="call-answer"]')
        sleep(10.0)
        if self.page.locator('[data-testid="default-mute-modal-toggle-camera"] span').count() == 2:
            self.page.click('[data-testid="default-mute-modal-toggle-camera"]')
            sleep(1.0)
        if self.page.locator('[data-testid="default-mute-modal-microphone-mute"] span').count() == 2:
            self.page.click('[data-testid="default-mute-modal-microphone-mute"]')
            sleep(1.0)
        self.page.click('[data-testid="default-mute-modal-confirm"]')

    def cinnox_get_call_id(self):
        try:
            elements = self.page.query_selector_all('xpath=//div[text()="Click to go to the call log"]')
            if len(elements) >= 2:
                elements[1].click()
            else:
                elements[0].click()
        except:
            pass

        self.page.click('[data-testid="chat-message-received-call-button-more-actions"]')
        self.page.click('[data-testid="copy-call-id-button"]')
        self.page.click('[aria-label="close"]')
        call_id = pyperclip.paste()
        # self.page.click('[data-testid="chatroom-editor"] div.public-DraftStyleDefault-block')
        # os_type = platform.system()
        # if os_type == 'Darwin': # Mac
        #     self.page.keyboard.press('Meta+V')
        # else:
        #     self.page.keyboard.press('Control+V')
        # self.page.click('[data-testid="send-message"]')
        # call_id = self.page.locator('[data-testid="message-sender-text-content"]').inner_text()
        self.lgr.info(f'[Call ID] {call_id}')
        return call_id

    def cinnox_bind_transfer(self, name):
        self.page.click('[data-testid="call-transfer"]')
        sleep(1.0)
        self.page.click('[data-testid="transfer-menu-blindTransfer-menu-item"]')
        sleep(1.0)
        self.page.fill('[data-testid="target-picker-search-staff-input"]', name)
        self.page.click('[data-testid="target-picker-card"]')
        sleep(5.0)

    def cinnox_warm_transfer(self, name):
        self.page.click('[data-testid="call-transfer"]')
        sleep(1.0)
        self.page.click('[data-testid="transfer-menu-warmTransfer-menu-item"]')
        sleep(1.0)
        self.page.fill('[data-testid="target-picker-search-staff-input"]', name)
        self.page.click('[data-testid="target-picker-card"]')
        sleep(5.0)

    def cinnox_confirm_warm_transfer(self):
        self.page.click('[data-testid="call-transfer"]')

    def cinnox_close_enquiry(self):
        self.page.click('[data-testid="room-header-submenu"]')
        self.page.click('[data-testid="more-menu-close-inquiry-this-room-menu-item-label"]')
        self.page.click('[data-testid="confirm-button"]')

    def cinnox_logout(self):
        self.page.click('[data-testid="topbar-profile-avatar"]')
        self.page.click('[data-testid="user-menu-logout-button"]')
        try:
            self.page.wait_for_selector('[data-testid="login-button"]', timeout=10000)
            self.lgr.info('[Cinnox] Logout successfully.')
        except:
            self.lgr.error('[Cinnox] Logout failed.')
            assert False

    def cxwv_direct_call_enquiry(self, url):
        self.go_to(url)
        self.page.click('[data-testid="engage-call-button"]', timeout=60000)
        self.lgr.info('[Cinnox] Go to CXWC')
        if self.env == 'BJ':
            try:
                # self.lgr.info('[Cinnox] Wait 60 seconds for BJ site pre-chat from')
                # self.page.click('[data-testid="visitor-form-submit"]', timeout=60000)
                # self.lgr.info('[Cinnox] Click on pre-chat from submit button')
                # sleep(0.5)
                self.lgr.info('[Cinnox] Wait 60 seconds for BJ site for end call button')
                self.page.wait_for_selector('[data-testid="call-end"]', timeout=60000)
            except:
                pass

        # elif self.env == 'JP':
        #     try:
        #         self.lgr.info('[Cinnox] Wait 60 seconds for BJ site pre-chat from')
        #         self.page.click('[label-id="visitor-form-submit"]', timeout=60000)
        #         self.lgr.info('[Cinnox] Click on pre-chat from submit button')
        #         sleep(0.5)
        #         self.lgr.info('[Cinnox] Wait 60 seconds for BJ site for end call button')
        #         self.page.wait_for_selector('[data-testid="call-end"]', timeout=60000)
        #     except:
        #         pass
        else:
            try:
                self.lgr.info('[Cinnox] Click on pre-chat from submit button')
                self.page.click('[data-testid="visitor-form-submit"]', timeout=10000)
            except:
                pass

    def cxwv_mute_call(self):
        self.page.click('[data-testid="call-mute"]')

    def control_center(self):
        import pyautogui
        pyautogui.keyDown('ctrl')

        # 模拟按下ArrowUp键
        pyautogui.press('up')

        # 等待一会儿，以确保键盘组合生效
        sleep(1)

        pyautogui.keyUp('ctrl')
