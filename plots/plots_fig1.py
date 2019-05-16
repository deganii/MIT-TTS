
import wave
import matplotlib.pyplot as plt
import numpy as np
audio_path = "C:/dev/6.345/Data/rna-composite.wav"
f = wave.open(audio_path, "rb")

# (nchannels, sampwidth, framerate, nframes, comptype, compname)
params = f.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]

str_data = f.readframes(nframes)
f.close()

wave_data = np.fromstring(str_data, dtype=np.short)
wave_data.shape = -1, 2
wave_data = wave_data.T
time = np.arange(0, nframes) * (1.0 / framerate)

figure = plt.gcf()  # get current figure
figure.set_size_inches(6, 3)

duration = nframes / float(framerate)
xticks = np.arange(0, duration, .1)
plt.subplot(211).set_xticks([])
plt.plot(time, wave_data[0] / 22000.)
plt.title('Google TTS', loc='left')

plt.subplot(212).set_xticks(xticks)
plt.plot(time, wave_data[1] / 25000., c="g")
plt.xlabel("time (ms)")
plt.title('Expert Speaker', loc='left')
# plt.savefig('quit.playing.games.png', dpi=100, bbox_inches='tight', pad_inches=0.1)
plt.show()
#plt.close(figure)