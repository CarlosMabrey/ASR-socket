# import socket
# from time import sleep

# # Server's IP address and port
# server_ip = '10.0.6.126'
# server_port = 9999

# # Create a socket object
# client_socket = socket.socket()

# # Connect to the server
# client_socket.connect((server_ip, server_port))

# # Receive the welcome message from the server
# welcome_message = client_socket.recv(1024).decode()
# print(welcome_message)

# # Loop to continuously receive input from the server
# # while True:
# #     # Receive data from the server
# #     data = client_socket.recv(1024).decode()
    
# #     # Check if the received data is empty
# #     if not data:
# #         break
    
# #     # Print the received data
# #     print(data)

# # Close the connection
# #client_socket.close()

# # Send data to the server

# for x in range(10000):
#     try:
#         client_socket.send(('This is super super super long text, how I expect ASR will be or similar. Some sort of quick redf fox jumped over a log or something.  ' + str(x)).encode()) 
#     except:
#         break
#     sleep(1)

# # Close the connection with the client 
# client_socket.close()

import sys
import queue
import threading
import sounddevice as sd
import espnet
from espnet2.bin.asr_inference_streaming import Speech2TextStreaming
from espnet_model_zoo.downloader import ModelDownloader
import argparse
import numpy as np
import wave
import queue
import socket
import time

tag='D-Keqi/espnet_asr_train_asr_streaming_transformer_raw_en_bpe500_sp_valid.acc.ave'
d=ModelDownloader()
speech2text = Speech2TextStreaming(
    **d.download_and_unpack(tag),
    token_type=None,
    bpemodel=None,
    maxlenratio=0.0,
    minlenratio=0.0,
    beam_size=20,
    ctc_weight=0.5,
    lm_weight=0.0,
    penalty=0.0,
    nbest=1,
    device = "cpu",
    disable_repetition_detection=True,
    decoder_text_length_limit=0,
    encoded_feat_length_limit=0
)

prev_lines = 0
# def progress_output(text, filename="output.txt"):
#     global prev_lines
#     lines=['']
#     for i in text:
#         if len(lines[-1]) > 100:
#             lines.append('')
#         lines[-1] += i
#     for i,line in enumerate(lines):
#         if i == prev_lines:
#             sys.stderr.write('\n\r')
#         else:
#             sys.stderr.write('\r\033[B\033[K')
#         sys.stderr.write(line)
#     with open(filename, 'w') as f:
#         for line in lines:
#             f.write(line + '\n')

#     prev_lines = len(lines)
#     sys.stderr.flush()


#     # try:
#     #     # Send the text over the socket with a delay
#     #     for char in text:
#     #         client_socket.sendall(char.encode())
#     #         time.sleep(0.01)  # delay of 0.01 seconds
#     # except:
#     #     print('Error sending the text to the server.')


def recognize(wavfile):
    with wave.open(wavfile, 'rb') as wavfile:
        ch=wavfile.getnchannels()
        bits=wavfile.getsampwidth()
        rate=wavfile.getframerate()
        nframes=wavfile.getnframes()
        buf = wavfile.readframes(-1)
        data=np.frombuffer(buf, dtype='int16')
    speech = data.astype(np.float16)/32767.0 #32767 is the upper limit of 16-bit binary numbers and is used for the normalization of int to float.
    sim_chunk_length = 640
    if sim_chunk_length > 0:
        for i in range(len(speech)//sim_chunk_length):
            results = speech2text(speech=speech[i*sim_chunk_length:(i+1)*sim_chunk_length], is_final=False)
            if results is not None and len(results) > 0:
                nbests = [text for text, token, token_int, hyp in results]
                text = nbests[0] if nbests is not None and len(nbests) > 0 else ""
                progress_output(nbests[0])
            else:
                progress_output("")
            
        results = speech2text(speech[(i+1)*sim_chunk_length:len(speech)], is_final=True)
    else:
        results = speech2text(speech, is_final=True)
    nbests = [text for text, token, token_int, hyp in results]
    progress_output(nbests[0])

def rec_sound(data, frames, time, status):
    global q
    q.put(data.astype(np.float16)/32767.0)

def asr():
    global q
    global keepWorking
    first = True

    while keepWorking:
        try:
            data = q.get(block=True, timeout=1 if not first else None)  # wait infinitely long on first call
            first = False
        except queue.Empty:
            break
        results = speech2text(speech=data, is_final=False)
        if results is not None and len(results) > 0:
            nbests = [text for text, token, token_int, hyp in results]
            text = nbests[0] if nbests is not None and len(nbests) > 0 else ""
            #print(nbests[0])
            progress_output(nbests[0])
        else:
            #pass
            progress_output("")
# seconds = 10

# q = queue.Queue()
# keepWorking = True
# t = threading.Thread(target=asr)
# t.start()
# count = 0
# print("start")
# with sd.InputStream(samplerate=16000, channels=1, blocksize=640, callback=rec_sound, dtype=np.int16):
#     sd.sleep(seconds*1000) # convert ms to s
# print("stop")
# keepWorking = False
# t.join()

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('10.0.6.126', 9999)

# Connect to the server
client_socket.connect(server_address)

# Sends progress output to the server

def progress_output(text, filename="output.txt"):
    global prev_lines
    lines=['']
    for i in text:
        if len(lines[-1]) > 100:
            lines.append('')
        lines[-1] += i
    for i,line in enumerate(lines):
        if i == prev_lines:
            sys.stderr.write('\n\r')
        else:
            sys.stderr.write('\r\033[B\033[K')
        sys.stderr.write(line)
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    prev_lines = len(lines)
    sys.stderr.flush()

    # Send the text over the socket
    try:
        client_socket.sendall(text.encode())
    except:
        print('Error sending the text to the server.')


# Start the ASR thread
seconds = 10

q = queue.Queue()
keepWorking = True
t = threading.Thread(target=asr)
t.start()
count = 0
print("start")
with sd.InputStream(samplerate=16000, channels=1, blocksize=640, callback=rec_sound, dtype=np.int16):
    sd.sleep(seconds*1000) # convert ms to s
print("stop")
keepWorking = False
t.join()

print("\n~~~~~~~~~~done~~~~~~~~~~")