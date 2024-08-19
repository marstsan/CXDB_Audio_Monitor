import platform
import soundcard as sc
import soundfile as sf
from lib.AudioVerification import AudioVerification

def recording(filename, lgr, time=10, sample_rate=44100):
    system = platform.system()
    if system == 'Darwin':
        lgr.info(f'{filename}.wav start recording...')
        with sc.get_microphone(id=str('Soundflower (2ch)'), include_loopback=True).recorder(samplerate=sample_rate) as mic:
            data = mic.record(numframes=sample_rate * time)
    else:
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sample_rate) as mic:
            data = mic.record(numframes=sample_rate * time)

    sf.write(file=f'audio_recording/{filename}.wav', data=data[:, 0], samplerate=sample_rate)
    lgr.info(f'{filename}.wav has been saved in the audio_recording folder.')