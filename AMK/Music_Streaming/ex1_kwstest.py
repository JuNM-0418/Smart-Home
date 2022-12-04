# pdf 61~62

#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""Example 1: GiGA Genie Keyword Spotting""" 

from __future__ import print_function 

import audioop
from ctypes import *
import RPi.GPIO as GPIO
import ktkws # KWS
import MicrophoneStream as MS
KWSID = ['기가지니', '지니야', '친구야', '자기야'] 
RATE = 16000
CHUNK = 512

GPIO.setmode(GPIO.BOARD) # GPIO 핀 설정 보드번호로 설정
GPIO.setwarnings(False) # setwarning false 오류방지
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP) #핀 입출력모드 지정
GPIO.setup(31, GPIO.OUT) #핀 입출력모드 지정
btn_status = False # 버튼이 눌려지지 않은 상태에서 시작

# 버튼이 눌려지면 btn_status를 True로 변경
def callback(channel): 
    print("falling edge detected from pin {}".format(channel)) 
    global btn_status 
    btn_status = True  
    print(btn_status)

GPIO.add_event_detect(29, GPIO.FALLING, callback=callback, bouncetime=10) 

# Error Handler
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p) 
def py_error_handler(filename, line, function, err, fmt): 
  dummy_var = 0
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler) 
asound = cdll.LoadLibrary('libasound.so') 
asound.snd_lib_error_set_handler(c_error_handler) 


# 마이크에서 음성을 받아서 호출어를 인식하는 함수
def detect(): 
    with MS.MicrophoneStream(RATE, CHUNK) as stream: 
        audio_generator = stream.generator() 

        for content in audio_generator: 
            

            rc = ktkws.detect(content)                                                              
            rms = audioop.rms(content,2) 
            #print('audio rms = %d' % (rms)) 

            # 마이크에서 음성을 받아서 호출어를 인식하면 1을 리턴
            if (rc == 1): 
                MS.play_file("../data/sample_sound.wav") # 호출어 인식시 음성 출력
                return 200 

# 버튼이 눌려지면 호출어를 인식하는 함수
def btn_detect(): 
    global btn_status 
    with MS.MicrophoneStream(RATE, CHUNK) as stream: 
        audio_generator = stream.generator() 

        for content in audio_generator: 
            GPIO.output(31, GPIO.HIGH) 
            rc = ktkws.detect(content) 
            rms = audioop.rms(content,2)                                                               
            #print('audio rms = %d' % (rms))
            GPIO.output(31, GPIO.LOW) 
            if (btn_status == True):
                rc = 1
                btn_status = False 
            if (rc == 1):
                GPIO.output(31, GPIO.HIGH) # 31번째 핀을 HIGH로 설정
                MS.play_file("../data/sample_sound.wav") # 음성파일 재생
                return 200 

def test(key_word = '기가지니'):
    rc = ktkws.init("../data/kwsmodel.pack") 
    print ('init rc = %d' % (rc))
    rc = ktkws.start()
    print ('start rc = %d' % (rc))
    print ('\n호출어를 불러보세요~\n')
    ktkws.set_keyword(KWSID.index(key_word)) 
    rc = detect()
    print ('detect rc = %d' % (rc))
    print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n') 
    ktkws.stop()
    return rc

def btn_test(key_word = '기가지니'): 
    global btn_status
    rc = ktkws.init("../data/kwsmodel.pack") 
    print ('init rc = %d' % (rc))
    rc = ktkws.start()
    print ('start rc = %d' % (rc)) 
    print ('\n버튼을 눌러보세요~\n')
    ktkws.set_keyword(KWSID.index(key_word)) 
    rc = btn_detect()
    print ('detect rc = %d' % (rc))                                                                            
    print ('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
    ktkws.stop() 
    return rc

def main(): 
    test()
if __name__ == '__main__': 
    main()