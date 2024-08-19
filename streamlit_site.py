import streamlit as st
import os
from PIL import Image
import subprocess


def remove_har_before_date(date, folder):
    if folder == 'audio_recording_old':
        command = ["find", folder, "-type", "f", "-name", "*.mp4", "!", "-newermt", f"{date} 23:59:59", "-exec", "rm",
                   "-f", "{}", ";"]
    else:

        command = ["find", folder, "-type", "f", "!", "-newermt", f"{date} 23:59:59", "-exec", "rm", "-f", "{}", ";"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()

    if process.returncode == 0:
        st.success(f"已成功移除 {date} 前的資料。")
    else:
        st.error(f"移除資料失敗。\n錯誤: {error.decode('utf-8')}")


def update_audio_db(action, audfprint_file, origin_recording_file):
    command = 'python'
    script = 'audfprint/audfprint.py'
    args = [action, '--dbase', f'audio_fprint/{audfprint_file}',
            f'audio_recording/error/{origin_recording_file}', '-N', '3']
    try:
        result = subprocess.run([command, script] + args, capture_output=True, text=True)
        st.write(args)
        if action == 'add':
            result_stdout = result.stdout
            if 'Added' in result_stdout:
                st.info('Added Successfully')
            else:
                st.error('Added Failed!')
        elif action == 'match':
            lines = result.stdout.split('\n')
            fourth_line = lines[3] if len(lines) > 3 else None
            if 'Matched' in fourth_line:
                st.info('Match')
            else:
                st.error('No Match!')
    except:
        st.error(f'Run subprocess error!\n{result}')


def main():
    audio_path = 'audio_recording/error'
    video_pth = 'video_screenshot/error'
    recording_path = 'audio_recording'
    screen_recording_path = 'ffmpeg_recording'
    logs_path = 'log'
    api_traces_path = 'api_traces'
    video_instruction = {
        "01": "StaffC 看不到 Visitor 的 camera 或 StaffC 看不到自己的 camera",
        "02": "Visitor 看不到 StaffC 的 camera 或 Visitor 看不到自己的 camera",
        "03": "StaffC 看不到 Visitor 的 screen share 或 StaffC 看不到自己的 screen share",
        "04": "Visitor 看不到 StaffC 的 screen share 或 Visitor 看不到自己的 screen share",
        "05": "StaffA 看不到 StaffC 的 camera",
        "06": "StaffC 看不到自己的 camera",
        "07": "Visitor 看不到 StaffC 的 camera",
        "08": "StaffA 看不到自己的 camera",
        "09": "StaffC 看不到 StaffA 的 camera",
        "10": "Visitor 看不到 StaffA 的 camera",
        "11": "StaffA 看不到 Visitor 的 camera",
        "12": "StaffC 看不到 Visitor 的 camera",
        "13": "Visitor 看不到自己的 camera",
        "14": "StaffA 看不到 StaffC 的 screen share",
        "15": "Visitor 看不到 StaffC 的 screen share"
    }
    table_data = [["文件名稱", "播放", "加入資料庫"]]
    # From here down is all the StreamLit UI.
    st.set_page_config(
        page_title="Audio Monitor Reports",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded")

    if "password" not in st.session_state:
        st.session_state["password"] = ''

    if "action" not in st.session_state:
        st.session_state["action"] = ''

    if "admin_password" not in st.session_state:
        st.session_state["admin_password"] = ''

    hcol1, hcol2, hcol3 = st.columns([1, 4, 1])

    with hcol2:
        hcol2.markdown("<h1 style='text-align: center; font-size: 48px;'>Audio Monitor Error Reports</h1>",
                       unsafe_allow_html=True)

    with hcol3:
        st.session_state["password"] = st.text_input('請輸入密碼', type='password')
        st.session_state["action"] = st.radio(
            "選擇 Action",
            ["match", "add"],
            index=0,
        )

    audio_tab, video_tab, recording_tab, quicktime_tab, logs_tab, api_tab, admin_tab, storage_tab = st.tabs(
        ["Audio", "Video Screenshot", "Recording", "Screen Recording", "Logs", "API Trace", "Administration", "Storage"])

    with audio_tab:
        file_list = [f for f in os.listdir(audio_path) if f.endswith(".wav")]
        file_list.sort(key=lambda x: os.path.getctime(os.path.join(audio_path, x)), reverse=True)
        # 添加列標題
        header_col1, header_col2, header_col3 = st.columns([1, 2.5, 0.5])
        with header_col1:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>文件名稱</h3>", unsafe_allow_html=True)

        with header_col2:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>播放</h3>", unsafe_allow_html=True)

        with header_col3:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>加入/比對資料庫</h3>", unsafe_allow_html=True)

        # 使用 columns 來創建類似表格的布局
        for selected_file in file_list:
            file_path = os.path.join(audio_path, selected_file)

            # 讀取文件內容
            with open(file_path, "rb") as file:
                file_contents = file.read()

            # 創建一行
            col1, col2, action_col, delete_col = st.columns([1, 2.5, 0.35, 0.1])
            # col1, col2, col3 = st.columns([1, 2.5, 0.5])
            with col1:
                st.text(selected_file)
            with col2:
                st.audio(file_contents, format="audio/wav")
            with action_col:
                button_key = f"{selected_file}"

                if st.button(f"執行", key=button_key, use_container_width=True):

                    # 檢查密碼是否正確
                    if st.session_state["password"] == 'm800':  # 將 '您的密碼' 替換為實際密碼
                        # 密碼正確，執行後續程式碼
                        if 'staffA' in button_key:
                            db = 'staffA.pklz'
                        elif 'staffB' in button_key:
                            db = 'staffB.pklz'
                        elif 'staffC' in button_key:
                            db = 'staffC.pklz'
                        elif 'visitor' in button_key:
                            db = 'visitor.pklz'
                        update_audio_db(st.session_state["action"], db, selected_file)
                    elif st.session_state["password"] == '':
                        st.error("請輸入密碼")
                    else:
                        st.error("密碼不正確")
            with delete_col:
                delete_button_key = f"delete_{selected_file}"

                if st.button("🗑️", key=delete_button_key, help='移除檔案'):
                    try:
                        if st.session_state["password"] == 'm800':
                            os.remove(file_path)
                            with col2:
                                st.toast(f"已成功刪除 {selected_file}")
                            st.balloons()
                            from time import sleep
                            sleep(2.5)
                            st.rerun()
                        elif st.session_state["password"] == '':
                            st.error("請輸入密碼!")
                        else:
                            st.error("密碼錯誤!")
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
            st.markdown('<hr style="border:1px solid #e6f0fa; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                        unsafe_allow_html=True)
    with video_tab:
        header_col1, header_col2 = st.columns([1, 2])
        with header_col1:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>文件名稱</h3>", unsafe_allow_html=True)

        with header_col2:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>截圖/錯誤說明</h3>", unsafe_allow_html=True)
        videofile_list = [f for f in os.listdir(video_pth) if f.endswith(".png")]
        videofile_list.sort(key=lambda x: os.path.getctime(os.path.join(video_pth, x)), reverse=True)

        for selected_videofile in videofile_list:
            file_path = os.path.join(video_pth, selected_videofile)
            image = Image.open(file_path)

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"<div style='text-indent: 18px;'>{selected_videofile}</div>", unsafe_allow_html=True)
                delete_button_key = f"delete_{selected_videofile}"

                if st.button("🗑️", key=delete_button_key, help='移除檔案'):
                    try:
                        if st.session_state["password"] == 'm800':
                            os.remove(file_path)
                            with col2:
                                st.toast(f"已成功刪除 {selected_videofile}")
                            st.balloons()
                            from time import sleep
                            sleep(2.5)
                            st.rerun()
                        elif st.session_state["password"] == '':
                            st.error("請輸入密碼!")
                        else:
                            st.error("密碼錯誤!")
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
            with col2:
                st.image(image)
                instruction = video_instruction[selected_videofile[0:2]]
                st.error(f'錯誤說明: {instruction}')
            st.markdown('<hr style="border:1px solid #e6f0fa; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                        unsafe_allow_html=True)
    with recording_tab:
        header_col1, header_col2 = st.columns([1, 2])
        with header_col1:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>文件名稱</h3>", unsafe_allow_html=True)

        with header_col2:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>錄音檔案</h3>", unsafe_allow_html=True)
        recordingfile_list = [f for f in os.listdir(recording_path) if f.endswith(".mp4")]
        recordingfile_list.sort(key=lambda x: os.path.getctime(os.path.join(recording_path, x)), reverse=True)

        for selected_recordingfile in recordingfile_list:
            file_path = os.path.join(recording_path, selected_recordingfile)
            with open(file_path, "rb") as file:
                file_contents = file.read()

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"<div style='text-indent: 18px;'>{selected_recordingfile}</div>", unsafe_allow_html=True)
                delete_button_key = f"delete_{selected_recordingfile}"

                if st.button("🗑️", key=delete_button_key, help='移除檔案'):
                    try:
                        if st.session_state["password"] == 'm800':
                            os.remove(file_path)
                            with col2:
                                st.toast(f"已成功刪除 {selected_recordingfile}")
                            st.balloons()
                            from time import sleep
                            sleep(2.5)
                            st.rerun()
                        elif st.session_state["password"] == '':
                            st.error("請輸入密碼!")
                        else:
                            st.error("密碼錯誤!")
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
            with col2:
                st.audio(file_contents, format="audio/mp4")
            st.markdown('<hr style="border:1px solid #e6f0fa; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                        unsafe_allow_html=True)
    with quicktime_tab:
        screen_recording_file_list = [f for f in os.listdir(screen_recording_path) if f.endswith(".mp4")]
        screen_recording_file_list.sort(key=lambda x: os.path.getctime(os.path.join(screen_recording_path, x)),
                                        reverse=True)
        header_col1, header_col2 = st.columns([1, 2])
        with header_col1:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>文件名稱</h3>", unsafe_allow_html=True)

        with header_col2:
            st.markdown("<h3 style='text-align: center; font-size: 16px;'>錄影檔案</h3>", unsafe_allow_html=True)

        for selected_recordingfile in screen_recording_file_list:
            file_path = os.path.join(screen_recording_path, selected_recordingfile)
            with open(file_path, "rb") as file:
                file_contents = file.read()

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"<div style='text-indent: 18px;'>{selected_recordingfile}</div>", unsafe_allow_html=True)
                delete_button_key = f"delete_{selected_recordingfile}"

                if st.button("🗑️", key=delete_button_key, help='移除檔案'):
                    try:
                        if st.session_state["password"] == 'm800':
                            os.remove(file_path)
                            with col2:
                                st.toast(f"已成功刪除 {selected_recordingfile}")
                            st.balloons()
                            from time import sleep
                            sleep(2.5)
                            st.rerun()
                        elif st.session_state["password"] == '':
                            st.error("請輸入密碼!")
                        else:
                            st.error("密碼錯誤!")
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")

            with col2:
                st.video(file_contents)
            st.markdown('<hr style="border:1px solid #e6f0fa; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                        unsafe_allow_html=True)
    with logs_tab:
        log_files = [f for f in os.listdir(logs_path) if f.endswith('.txt')]
        log_files.sort(key=lambda x: os.path.getctime(os.path.join(logs_path, x)), reverse=True)
        selected_file = st.selectbox('選擇 Logs 文件', log_files, index=None)
        # 當用戶選擇一個文件時，讀取並顯示其內容
        if selected_file:
            file_path = os.path.join(logs_path, selected_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            # st.write(file_content)
            file_content_md = file_content.replace('\n', '\n\n')
            # st.markdown(file_content_md)
            st.markdown(f"<p style='font-size: 12px;'>{file_content_md}</p>", unsafe_allow_html=True)
    with api_tab:
        api_tabcol1, api_tabcol2, api_tabcol3, api_tabcol4 = st.columns([1, 1, 1, 1])
        browser1_traces_path = api_traces_path + '/browser1'
        browser2_traces_path = api_traces_path + '/browser2'
        browser3_traces_path = api_traces_path + '/browser3'
        browser4_traces_path = api_traces_path + '/browser4'

        with api_tabcol1:
            browser1_traces = [f for f in os.listdir(browser1_traces_path) if f.endswith('.zip')]
            browser1_traces.sort(key=lambda x: os.path.getctime(os.path.join(browser1_traces_path, x)), reverse=True)
            browser1_selected_file = st.selectbox('Browser1', browser1_traces, index=None, placeholder="Select file", )

            if browser1_selected_file:
                download_file_path = os.path.join(browser1_traces_path + '/', browser1_selected_file)
                try:
                    with open(download_file_path, "rb") as file:
                        file_bytes = file.read()  # 讀取文件的二進制數據
                        btn1 = st.download_button(
                            label="Download file",
                            data=file_bytes,  # 提供文件的二進制數據
                            file_name=f'browser1_{browser1_selected_file}',
                            mime="application/zip"  # 確保 MIME 類型設定為 ZIP
                        )
                except Exception as e:
                    st.error(f"Error downloading file: {e}")

        with api_tabcol2:
            browser2_traces = [f for f in os.listdir(browser2_traces_path) if f.endswith('.zip')]
            browser2_traces.sort(key=lambda x: os.path.getctime(os.path.join(browser2_traces_path, x)), reverse=True)
            browser2_selected_file = st.selectbox('Browser2', browser2_traces, index=None, placeholder="Select file", )

            if browser2_selected_file:
                download_file_path = os.path.join(browser2_traces_path + '/', browser2_selected_file)
                try:
                    with open(download_file_path, "rb") as file:
                        file_bytes = file.read()  # 讀取文件的二進制數據
                        btn2 = st.download_button(
                            label="Download file",
                            data=file_bytes,  # 提供文件的二進制數據
                            file_name=f'browser2_{browser2_selected_file}',
                            mime="application/zip"  # 確保 MIME 類型設定為 ZIP
                        )
                except Exception as e:
                    st.error(f"Error downloading file: {e}")

        with api_tabcol3:
            browser3_traces = [f for f in os.listdir(browser3_traces_path) if f.endswith('.zip')]
            browser3_traces.sort(key=lambda x: os.path.getctime(os.path.join(browser3_traces_path, x)), reverse=True)
            browser3_selected_file = st.selectbox('Browser3', browser3_traces, index=None, placeholder="Select file", )

            if browser3_selected_file:
                download_file_path = os.path.join(browser3_traces_path + '/', browser3_selected_file)
                try:
                    with open(download_file_path, "rb") as file:
                        file_bytes = file.read()  # 讀取文件的二進制數據
                        btn3 = st.download_button(
                            label="Download file",
                            data=file_bytes,  # 提供文件的二進制數據
                            file_name=f'browser3_{browser3_selected_file}',
                            mime="application/zip"  # 確保 MIME 類型設定為 ZIP
                        )
                except Exception as e:
                    st.error(f"Error downloading file: {e}")

        with api_tabcol4:
            browser4_traces = [f for f in os.listdir(browser4_traces_path) if f.endswith('.zip')]
            browser4_traces.sort(key=lambda x: os.path.getctime(os.path.join(browser4_traces_path, x)), reverse=True)
            browser4_selected_file = st.selectbox('Browser4', browser4_traces, index=None, placeholder="Select file", )

            if browser4_selected_file:
                download_file_path = os.path.join(browser4_traces_path + '/', browser4_selected_file)
                try:
                    with open(download_file_path, "rb") as file:
                        file_bytes = file.read()  # 讀取文件的二進制數據
                        btn4 = st.download_button(
                            label="Download file",
                            data=file_bytes,  # 提供文件的二進制數據
                            file_name=f'browser4_{browser4_selected_file}',
                            mime="application/zip"  # 確保 MIME 類型設定為 ZIP
                        )
                except Exception as e:
                    st.error(f"Error downloading file: {e}")

        st.link_button("Playwright Trace Viewer", "https://trace.playwright.dev/")
    with admin_tab:
        if st.session_state["password"] == 'm8001':
            st.success('Hello 管理者 👋')
            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 Logs 檔案</p>",
                                  help='移除 n 天前的 Logs 檔案', unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        # st.write('天數設定（必須大於或等於7）')
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='log_day')
                        if st.button("執行", key='log_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'log')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 Video Error 檔案</p>",
                                  help='移除 n 天前的 Video Error 檔案',
                                  unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        # st.write('天數設定（必須大於或等於7）')
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='vidoe_day')
                        if st.button("執行", key='vidoe_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'video_screenshot/error')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 Audio Error 檔案</p>",
                                  help='移除 n 天前的 Audio Error 檔案',
                                  unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='audio_day')
                        if st.button("執行", key='audio_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'audio_recording/error')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 Recording 檔案</p>",
                                  help='移除 n 天前的 Recording 檔案',
                                  unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='recording_day')
                        if st.button("執行", key='recording_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'audio_recording')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 Screen Recording 檔案</p>",
                                  help='移除 n 天前的 Recording 檔案',
                                  unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='screen_recording_day')
                        if st.button("執行", key='screen_recording_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'ffmpeg_recording')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

            with st.container():
                col1, col2 = st.columns([2, 4])

                with col1:
                    col1.markdown("<p style='text-align: left; font-size: 18px;'>移除 API Trace 檔案</p>",
                                  help='移除 n 天前的 API Trace 檔案',
                                  unsafe_allow_html=True)
                with col2:
                    with st.expander("移除天數"):
                        from datetime import datetime, timedelta
                        st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                                    unsafe_allow_html=True)
                        st.session_state["admin_password"] = st.text_input("天數設定（必須大於或等於7）", 7,
                                                                           key='API_trace_day')
                        if st.button("執行", key='API_trace_days'):
                            try:
                                # 嘗試將輸入轉換為數字
                                value = float(st.session_state["admin_password"])
                                if value < 7:
                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=7))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    st.error(f"只能移除 7 天前({modify_date})的資料。")
                                else:

                                    today = datetime.today()
                                    remove_date = (today - timedelta(days=value))
                                    modify_date = remove_date.strftime('%Y-%m-%d')
                                    remove_har_before_date(modify_date, 'api_traces/browser1')
                                    remove_har_before_date(modify_date, 'api_traces/browser2')
                                    remove_har_before_date(modify_date, 'api_traces/browser3')
                                    remove_har_before_date(modify_date, 'api_traces/browser4')

                            except ValueError:
                                # 如果輸入不能轉換為數字
                                st.error("請輸入有效的數字。")

                st.markdown('<hr style="border:1px solid #f0f8ff; margin-top: 0.5rem; margin-bottom: 0.5rem"/>',
                            unsafe_allow_html=True)

        else:
            st.info("此頁內容受保護。")
    with storage_tab:
        import plotly.express as px
        def calculate_folder_size(folder_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            total_size_mb = total_size / (1024 * 1024)
            return total_size_mb

        # 定義資料夾路徑
        folders = ["api_traces", "log",
                   "video_screenshot/error", "audio_recording",
                   "ffmpeg_recording"]

        # 計算每個資料夾的大小
        sizes = [calculate_folder_size(folder) for folder in folders]

        labels = ["API Trace", "Log", "Video Screenshot", "Audio Recording", "Ffmpeg Recording"]
        fig = px.pie(values=sizes, names=labels, title="檔案容量")

        # 更新標籤，使其包含 MB 容量
        fig.update_traces(textinfo='percent+label', hoverinfo='label+value',
                          hovertemplate='%{label}<br>%{value:.2f} MB')

        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
