# p90 

# import library
from __future__ import print_function

import grpc
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import audioop
import os
from ctypes import * 

HOST = 'gate.gigagenie.ai'
PORT = 4080 
RATE = 16000 
CHUNK = 512

# TTS : getText2VoiceStream
def getText2VoiceStream(inText,inFileName):

    channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials()) 
    stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)

    message = gigagenieRPC_pb2.reqText()
    message.lang=0
    message.mode=0
    message.text=inText
    writeFile=open(inFileName,'wb')
    for response in stub.getText2VoiceStream(message): 
        if response.HasField("resOptions"):
            print ("\n\nResVoiceResult: %d" %(response.resOptions.resultCd)) 
        if response.HasField("audioContent"):
            print ("Audio Stream\n\n")
            writeFile.write(response.audioContent)
    writeFile.close()
    return response.resOptions.resultCd 

def main():
    output_file = "testtts.wav"
    getText2VoiceStream("안녕하세요. 반갑습니다.", output_file) 
    MS.play_file(output_file)
    print( output_file + "이 생성되었으니 파일을 확인바랍니다. \n\n\n")
                                
if __name__ == '__main__': 
    main()