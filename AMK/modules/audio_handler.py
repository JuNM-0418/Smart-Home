from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
from threading import Thread

class TTS:
    def __init__(self, lang: str = "ko", filename: str = "audio_dump.mp3"):
        self.lang = lang
        self.filename = filename

    def gen_tts(self, text: str):
        audio = gTTS(text, lang=self.lang)
        audio.save(self.filename)

    def direct_tts(self, text: str, wait: bool = True):
        self.gen_tts(text)
        thr = Thread(target=playsound, args=(self.filename, ))
        thr.start()
        if wait:
            thr.join()
        return thr

class STT(sr.Recognizer):
    def __init__(self, timeout=10, phase=10, lang: str = "ko-KR"):
        self.lang = lang
        super().__init__()

    def get_text(self, timeout=10, phrase=10):
        try:
            with sr.Microphone() as source:
                audio = self.listen(source, timeout=timeout,
                                    phrase_time_limit=phrase)
            return self.recognize_google(audio, language=self.lang)
        except sr.UnknownValueError:
            print("recognize failed")
        except sr.RequestError as e:
            print(e.with_traceback())
        return None

if __name__ == "__main__":
    from datetime import datetime
    stt = STT()
    tts = TTS()
            
    now = datetime.now().strftime("%Y년 %m월 %d일")
    tts.direct_tts(f"안녕하세요. 테스트입니다. 현재 시간은 {now} 입니다.")
