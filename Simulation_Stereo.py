import cvlib as cv
from cvlib.object_detection import draw_bbox
from cvlib.object_detection import detect_common_objects
import cv2
import numpy as np




# Traitement video -------------------------------------------------------------------------------------------------------


Pos=[]

Height,Weight=720,528
video_path = "Projet Anglais.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error in opening video capture")
else :
    fps = cap.get(cv2.CAP_PROP_FPS)             # Nombre de frames par seconde
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps                # Durée totale en secondes

    print(f"Durée de la vidéo : {duration:.2f} s, FPS : {fps}")
    

    interval = 5  # secondes
    timestamps = np.arange(0, duration, interval)

    for t in timestamps:
        frame_index = int(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            continue
        frame_resize=cv2.resize(frame,(Height, Weight),interpolation=cv2.INTER_CUBIC)
        faces,face_confidences=cv.detect_face(frame_resize)
        x_center=0
        y_center=0
        for face, conf in zip(faces, face_confidences):
                (startX, startY) = face[0], face[1]
                (endX, endY) = face[2], face[3]
                cv2.rectangle(frame_resize, (startX, startY), (endX, endY), (255, 0, 0), 2) # Blue color for faces
                x_center=(endX+startX)/(2*Height)
                y_center=(endY+startY)/(2*Weight)
                cv2.putText(frame_resize,f"Position: ({x_center:.2f},{y_center:.2f})",(startX,startY),cv2.FONT_HERSHEY_PLAIN,1.0,(0,255,0),1)
                
        
            # Display the output
        cv2.imshow('Object Detection', frame_resize)
        cv2.waitKey(1000)
        # 🔍 Ici tu fais ta détection de visage sur "frame"
        print(f"Traitement à t = {t:.1f} s, frame {frame_index}",f"Position: ({x_center:.2f},{y_center:.2f})")
        Pos.append((x_center,y_center))

cap.release()
cv2.destroyAllWindows()




# Traitement audio ------------------------------------------------------------------------------------------------



import pyroomacoustics as pra

import sounddevice as sd
import librosa

# Charger un fichier MP3 ou WAV
audio, fs = librosa.load("Projet_anglais_audio.wav", sr=None)

# Définir la salle
longueur=6;largeur=4;hauteur=3
room_dim = [longueur, largeur, hauteur]
room = pra.ShoeBox(room_dim, fs=fs, absorption=0.4, max_order=3,mics=[[4,2,1.5]])

# Ajouter les microphones (public)
mic_positions = np.array([[4, 2, 1.5]]).T  # 1 micro
room.add_microphone_array(mic_positions)




# Tableau pour stocker l’audio modifié en temps réel
audio_dynamic = np.zeros_like(audio)
i=0
# Simuler le mouvement en temps réel
for t in timestamps:
    # Position évolutive de la source
   
    x=Pos[i][0]*longueur
    y=Pos[i][1]*largeur
    i=i+1

    # Supprimer toutes les anciennes sources
    room.sources = []
    # Ajouter la source avec une portion de l'audio
    start = int(t * fs)
    end = min(int((t + interval) * fs), len(audio)-1)
    room.add_source([x, y, 1.5], signal=audio[start:end])

    # Simuler la salle
    room.simulate()

    # Récupérer le son modifié
    mic_signal = room.mic_array.signals[0, :]

    # Ajuster la taille du signal
    if len(mic_signal) > (end - start):  
        mic_signal = mic_signal[:(end - start)]  # Tronquer si trop long
    elif len(mic_signal) < (end - start):
        mic_signal = np.pad(mic_signal, (0, (end - start) - len(mic_signal)), mode='constant')  # Compléter avec des zéros

    # Stocker dans l'audio dynamique
    audio_dynamic[start:end] = mic_signal
# Normaliser et jouer le son modifié
audio_dynamic = audio_dynamic / np.max(np.abs(audio_dynamic))
sd.play(audio_dynamic, samplerate=fs)
sd.wait()





# Asssemblage video et audio modifié

"""
from moviepy.editor import VideoFileClip, AudioFileClip

video = VideoFileClip("video.mp4")
audio = AudioFileClip("audio_processed.wav")

# Associer le nouvel audio à la vidéo
video_with_new_audio = video.set_audio(audio)

# Exporter le nouveau fichier vidéo
video_with_new_audio.write_videofile("video_finale.mp4", codec="libx264", audio_codec="aac")

"""