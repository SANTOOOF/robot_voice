import os
import csv

audio_dir = "robot_voice_dataset/audio"
labels = {
    "avance": "AVANCER",
    "stop": "STOP",
    "gauche": "GAUCHE",
    "droite": "DROITE",
}

with open("robot_voice_dataset/metadata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["file", "text", "label"])

    for file in os.listdir(audio_dir):
        for key in labels:
            if file.startswith(key):
                writer.writerow([f"audio/{file}", key, labels[key]])
