import srt
import os
from pydub import AudioSegment
import csv

with open('MIT5_07SCF13_JoAnne_Redox_300k.srt', 'r') as myfile:
  data = myfile.read()

srt_data = list(srt.parse(data))
wfile = AudioSegment.from_wav('MIT5_07SCF13_JoAnne_Redox_300k-22.5kHz-mono.wav')

# split up the wav files, and create a metadata.csv
os.makedirs('wavs', exist_ok=True)
with open('metadata.csv', 'w', newline='') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter='|',
    quotechar='"', quoting=csv.QUOTE_MINIMAL)
  for idx, sd in enumerate(srt_data):
    id = "07SCF13-JS-{0:04d}".format(idx)
    content = sd.content.replace('\n', ' ').replace('\r', '')
    st = int(sd.start.total_seconds() * 1000)
    end = int(sd.end.total_seconds() * 1000)
    clip = wfile[st:end]
    clip.export("data/{0}.wav".format(id), format="wav")
    csvwriter.writerow([id, content, content])

comp = srt.compose(srt_data)
print(comp)
