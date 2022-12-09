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
    def __init__(self, timeout=7, phrase=7,lang: str = "ko-KR"):
    
        self.lang = lang
        super().__init__()

    def get_text(self, timeout=7, phrase=7):
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
    # from datetime import datetime
    import datetime
    stt = STT()
    tts = TTS()
            
    # now = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    now = datetime.datetime.now().strftime("%H시 %M분")
    after = datetime.datetime.now() + datetime.timedelta(minutes=20)
    alarm = after.strftime("%H시 %M분")

    print(now)
    print(alarm)
    

    tts.direct_tts(f"현재 시간은 {now} 입니다.")
    tts.direct_tts(f"알람 시간은 {alarm} 입니다.")


