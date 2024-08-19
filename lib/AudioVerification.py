import subprocess
import numpy as np
import librosa
import platform
import soundcard as sc
import soundfile as sf


class AudioVerification:
    def __init__(self, recording_file=None, call_id=None, lgr=None):
        self.lgr = lgr
        self.command = 'python'
        self.script = 'audfprint/audfprint.py'
        self.origin_recording_file = recording_file
        if recording_file is not None:
            self.audfprint_file = recording_file.split('_')[1]
            self.recording_file = recording_file.split('_')[1]
            self.args = ['match', '--dbase', f'audio_fprint/{self.audfprint_file}.pklz', f'audio_recording/{self.origin_recording_file}.wav', '-N', '3']
        self.call_id = call_id


    def recording(self, time=10, sample_rate=44100):
        system = platform.system()
        self.lgr.info(f'{self.origin_recording_file}.wav start recording...')
        if system == 'Darwin':
            try:
                with sc.get_microphone(id='BlackHole 2ch', include_loopback=True).recorder(samplerate=sample_rate) as mic:
                    data = mic.record(numframes=sample_rate * time)
            except Exception as e:
                print("Error:", e)
        else:
            try:
                with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sample_rate) as mic:
                    data = mic.record(numframes=sample_rate * time)
            except Exception as e:
                print("Error:", e)

        sf.write(file=f'audio_recording/{self.origin_recording_file}.wav', data=data[:, 0], samplerate=sample_rate)
        self.lgr.info(f'{self.origin_recording_file}.wav has been saved in the audio_recording folder.')

    def get_audfprint_verification_result(self):
        self.recording()
        self.lgr.info(f'[Audio Verification Result] {self.origin_recording_file}.wav Verifying...')
        result = subprocess.run([self.command, self.script] + self.args, capture_output=True, text=True)
        lines = result.stdout.split('\n')
        fourth_line = lines[3] if len(lines) > 3 else None
        if 'Matched' in fourth_line:
            self.lgr.info(f'[Audio Verification Result] {self.origin_recording_file}.wav matched.')
            return True
        else:
            import shutil
            from datetime import datetime, timedelta
            time_stamp = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H-%M-%SZ')
            shutil.copy(f'audio_recording/{self.origin_recording_file}.wav', f'audio_recording/error/{self.origin_recording_file}_{time_stamp}.wav')
            self.lgr.info(f'[Audio Verification Result] {self.origin_recording_file} no match found.')
            return False

    def get_decibel_verification_result(self):
        y, sr = librosa.load(f"audio_recording/{self.call_id}.mp4", sr=None)
        rms_value = np.sqrt(np.mean(y ** 2))
        if rms_value != 0:
            db_value = 20 * np.log10(rms_value)
        else:
            db_value = -np.inf

        if -30 < db_value < -20:
            self.lgr.info(f'[Decibel Verification Result] Passed (dB: {round(db_value, 2)})')
            return True
        else:
            self.lgr.info(f'[Decibel Verification Result] Failed (dB: {round(db_value, 2)})')
            return False
