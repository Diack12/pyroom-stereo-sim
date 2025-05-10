import sounddevice as sd
import queue
import numpy as np
import cv2 
import pyroomacoustics as pra
import cvlib as cv



def precalculate_rirs_stereo(xmax, ymax, z=1.5, dx=0.1, dy=0.1, room_dim=[6,5,3], fs=44100):
    x_values = np.arange(0, xmax, dx)
    y_values = np.arange(0, ymax, dy)
    rir_map = {}
    for x in x_values:
        for y in y_values:
            room = pra.ShoeBox(room_dim, fs=fs, absorption=0.5, max_order=3)
            mic_positions = np.array([
                [4,   7],
                [5, 5],
                [1.5, 1.5]
            ])
            room.add_microphone_array(pra.MicrophoneArray(mic_positions, fs=fs))
            room.add_source([x, y, z])
            room.compute_rir()
            rir_left = room.rir[0][0]
            rir_right = room.rir[1][0]
            rir_map[(round(x,3), round(y,3))] = (rir_left, rir_right)
    return rir_map

def get_rirs_from_face(x_norm, y_norm, xmax, ymax, dx, dy, rir_map):
    x = round(x_norm * xmax, 2)
    y = round(y_norm * ymax, 2)
    xq = round(np.floor(x / dx) * dx, 3)
    yq = round(np.floor(y / dy) * dy, 3)
    return rir_map.get((xq, yq), (np.zeros(2048), np.zeros(2048)))

def Face_Position(frame,Height=720,Weight=528):
    frame_resize=cv2.resize(frame,(Height, Weight),interpolation=cv2.INTER_CUBIC)
    faces,face_confidences=cv.detect_face(frame_resize)
    x_center=y_center=0
    startX=startY=endX=endY=0
    for face, conf in zip(faces, face_confidences):
        (startX, startY) = face[0], face[1]
        (endX, endY) = face[2], face[3]
        x_center=(endX+startX)/(2*Height)
        y_center=(endY+startY)/(2*Weight)
    return x_center,y_center,startX,startY,endX,endY

def draw_room_view(x, y, xmax=6, ymax=4, grid_step=0.1, mic_pos=((2.5, 2), (3.1, 2)), scale=100):
    width = int(xmax * scale)
    height = int(ymax * scale)
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255
    for gx in np.arange(0, xmax + grid_step, grid_step):
        x_px = int(gx * scale)
        cv2.line(canvas, (x_px, 0), (x_px, height), (220, 220, 220), 1)
    for gy in np.arange(0, ymax + grid_step, grid_step):
        y_px = int(gy * scale)
        cv2.line(canvas, (0, y_px), (width, y_px), (220, 220, 220), 1)
    # Position des micros
    for mx, my in mic_pos:
        mic_x, mic_y = int(mx * scale), int(my * scale)
        cv2.circle(canvas, (mic_x, mic_y), 6, (0, 0, 255), -1)
    cv2.putText(canvas, "Salle (vue du dessus)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    return canvas

SampleRate=16000
sd.default.samplerate=SampleRate
blocksize=1024
sd.default.blocksize=blocksize
longueur,largeur,hauteur=10,10,3
Height,Weight=720,528
room_dim = [longueur, largeur, hauteur]
rir_map = precalculate_rirs_stereo(xmax=longueur, ymax=largeur, z=hauteur, dx=0.1, dy=0.1, room_dim=room_dim, fs=SampleRate)

class AudioProcessor:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.rir_left = np.zeros(2048)
        self.rir_right = np.zeros(2048)
        self.prev_key = None
        self.tail = np.zeros(2048)

    def __call__(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        key = (round(self.x, 2), round(self.y, 2))
        if key != self.prev_key:
            self.rir_left, self.rir_right = get_rirs_from_face(self.x, self.y, longueur, largeur, 0.1, 0.1, rir_map)
            self.prev_key = key
        dry = indata[:, 0]
        full_input = np.concatenate((self.tail, dry))
        wet_left = np.convolve(full_input, self.rir_left, mode='full')[:len(dry)]
        wet_right = np.convolve(full_input, self.rir_right, mode='full')[:len(dry)]
        outdata[:, 0] = wet_left
        outdata[:, 1] = wet_right
        self.tail = full_input[-max(len(self.rir_left), len(self.rir_right)):] 

audio_processor=AudioProcessor()
scale=100
canvas=draw_room_view(0, 0, xmax=longueur, ymax=largeur, grid_step=0.1, mic_pos=((4, 5), (7, 5)), scale=scale)

stream=sd.Stream(callback=audio_processor,samplerate=SampleRate,blocksize=blocksize,channels=(1,2),device=(1,3))
cap=cv2.VideoCapture(0)
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.namedWindow("canvas", cv2.WINDOW_NORMAL)

with stream:
    while True:
        ret,frame=cap.read()
        audio_processor.x,audio_processor.y,startX,startY,endX,endY=Face_Position(frame)

        frame_resize=cv2.resize(frame,(Height, Weight),interpolation=cv2.INTER_CUBIC)
        cv2.rectangle(frame_resize, (startX, startY), (endX, endY), (255, 0, 0), 2)
        cv2.imshow('frame',frame_resize)


        canva_copy=canvas.copy()
        source_x = int(audio_processor.x * longueur * scale)
        source_y = int(audio_processor.y * largeur * scale)
        cv2.circle(canva_copy, (source_x, source_y), 6, (0, 255, 0), -1)
        cv2.imshow('canvas',canva_copy)

        if cv2.waitKey(1) & 0xFF==ord('q'):
            break
