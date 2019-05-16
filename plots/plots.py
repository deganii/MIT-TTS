import wave
import srt
from pydub import AudioSegment
import matplotlib.pyplot as plt
import wave
import numpy as np

audio_path = "data/raw/MIT5_07SCF13_JoAnne_Intro.wav"
srt_path = "data/raw/MIT5_07SCF13_JoAnne_Intro.srt"
# aligned_path = "data/raw/MIT5_07SCF13_JoAnne_Intro.aligned.srt"
aligned_path = "data/raw/MIT5_07SCF13_JoAnne_Intro.trimmed.srt"

with open(srt_path, 'r') as srt_file:
    srt_str = srt_file.read()
with open(aligned_path, 'r') as srt_file:
    aligned_str = srt_file.read()

srt_data = list(srt.parse(srt_str))
aligned_data = list(srt.parse(aligned_str))

# wfile = AudioSegment.from_wav(audio_path)
# time = wfile.duration_seconds
#
# st = int(sd.start.total_seconds() * 1000)
# end = int(sd.end.total_seconds() * 1000)
# clip = wfile[st:end]

# look for where the text matches
pairs = {}
for item in srt_data:
    pair = next((x for x in aligned_data
        if x.content == item.content), None)
        # if x.content.strip().startswith(item.content.replace('\n',' ').strip())),None)
    if pair is not None:
        pairs[item.content] = (item,pair)

f = wave.open(audio_path, "rb")

# (nchannels, sampwidth, framerate, nframes, comptype, compname)
params = f.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]

str_data = f.readframes(nframes)
f.close()

wave_data = np.fromstring(str_data, dtype=np.short)
#wave_data.shape = -1, 1
wave_data = wave_data.T
# wave_data = wave_data
time = np.arange(0, nframes) * (1.0 / framerate)



fig,ax = plt.subplots(1)
#pl.subplot(211)


for content, (cc, align) in pairs.items():
    st, end = cc.start.total_seconds(), cc.end.total_seconds()
    st_a, end_a = align.start.total_seconds(), align.end.total_seconds()

    # plt.axvline(x=cc.start.total_seconds(), color='b')
    # plt.axvline(x=align.start.total_seconds(), color='r')
    #
    # plt.axvline(x=cc.end.total_seconds(), color='b')
    # plt.axvline(x=align.end.total_seconds(), color='r')
    #
    rect = plt.Rectangle((st_a,0.0), end_a-st_a, 10000.0,
                  color='b', alpha=0.3)
    plt.text(st_a, 11000, content)
    ax.add_patch(rect)
    rect = plt.Rectangle((st,-10000.0), end-st, 10000.0,
                  color='r', alpha=0.4)
    ax.add_patch(rect)
    plt.text(st, -11000, content)

plt.plot(time, wave_data)
plt.xlabel("time (seconds)")
plt.show()