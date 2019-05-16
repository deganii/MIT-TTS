import os
from pydub import AudioSegment
import csv
import subprocess
import urllib.request
import srt
import datetime
from datetime import timedelta

def path_from_url(url):
  return 'data/raw/' + url.rsplit('/', 1)[1]

def download_audio(video_url, save_path=None,
                  sample_rate=22050, channels=1):
  temp_path = path_from_url(video_url)
  audio_path = save_path + '.wav'
  urllib.request.urlretrieve(video_url, temp_path)
  # -f s16le
  command = "ffmpeg -i {0} -ar {1} -ac {2} -vn {3}"\
    .format(temp_path, sample_rate, channels, save_path)
  subprocess.call(command, shell=True)
  os.remove(temp_path)
  return audio_path

def download_srt(srt_url, save_path=None):
  if save_path is None:
    save_path = path_from_url(srt_url)
  urllib.request.urlretrieve(srt_url, save_path)

# use aeneas to align audio automagically
# def align_audio(text_path, audio_path):
  # import aeneas
  # aeneas.tools.execute_task

def download_raw_data():
  os.makedirs('data/raw', exist_ok=True)
  with open('data/data_sources.csv', 'r') as ds_file:
    csv_reader = csv.reader(ds_file, delimiter=',')
    next(csv_reader)  # skip the header
    # read the names in data sources
    for name, video, srt in csv_reader:
      download_audio(video, "data/raw/{0}.wav".format(name))
      download_srt(srt, "data/raw/{0}.srt".format(name))

# trim silence from the beginning and end of a clip
def trim_silence(clip, window_ms=50, hop = 20, thresh_dB = -50.0): # all in ms
  def trim(clip):
    trim_ms = 0.0
    while clip[trim_ms:trim_ms + window_ms].dBFS < thresh_dB and trim_ms < len(clip):
      trim_ms += hop
    return trim_ms
  start_trim, end_trim = trim(clip), trim(clip.reverse())
  return clip[start_trim:len(clip) - end_trim], start_trim, end_trim


# create a dataset from a list of srt/audio pairs
def create_dataset(data_source='data/data_sources.csv',
    output_path='data/', force_aligned=False, trim=False):
  # if(os.path.exists(output_path+'wavs')):
  #   os.remove(output_path + 'wavs', )
  os.makedirs(output_path + 'wavs', exist_ok=True)

  # split up the wav files, and create a metadata.csv
  with open(output_path+'metadata.csv', 'w', newline='') as meta_file:
    csvwriter = csv.writer(meta_file, delimiter='|',
      quotechar='"', quoting=csv.QUOTE_MINIMAL)
    counter = 0
    duration = 0
    with open(data_source, 'r') as ds_file:
      csv_reader = csv.reader(ds_file, delimiter=',')
      next(csv_reader) # skip the header
      # read the names in data sources
      for name, video_url, srt_url in csv_reader:
        audio_path = "data/raw/{0}.wav".format(name)
        if force_aligned:
          srt_path = "data/raw/{0}.aligned.srt".format(name)
        else:
          srt_path = "data/raw/{0}.srt".format(name)

        with open(srt_path, 'r') as srt_file:
          data = srt_file.read()
        srt_data = list(srt.parse(data))
        wfile = AudioSegment.from_wav(audio_path)

        for idx, sd in enumerate(srt_data):
          # skip empty strings and the OCW preamble
          if idx > 7 and sd.content.strip():
            id = "{0:04d}-{1}".format(counter, name)
            content = sd.content.replace('\n', ' ').replace('\r', '')

            # replace speaker identification text
            content = content.replace("PROFESSOR: ", "")
            content = content.replace("JOANNE STUBBE: ", "")
            content = content.replace("SPEAKER 1:", "")

            st = int(sd.start.total_seconds() * 1000)
            end = int(sd.end.total_seconds() * 1000)
            clip = wfile[st:end]
            wav_path = output_path+"wavs/{0}.wav".format(id)

            # trim silence using librosa for better quality
            if trim:
              clip, new_st, new_end = trim_silence(clip)
              sd.start = sd.start + timedelta(milliseconds=new_st)
              sd.end = sd.end - timedelta(milliseconds=new_end)
              if new_st != 0 or new_end != 0:
                print("{2:04d} Trimmed: ({0},{1})".format(new_st, new_end, counter))

            clip.export(wav_path, format="wav")

            # put an extra column in case we need to adjust the text
            csvwriter.writerow([id, content, content])
            counter = counter+1
            duration = duration + len(clip)
        if trim:
          trim_path = "data/raw/{0}.trimmed.srt".format(name)
          with open(trim_path, 'w') as srt_trim:
            srt_trim.write(srt.compose(srt_data))
        print("Total Utterances: {0}, Total Length: {1} minutes".format(counter, duration / 60000.0))

# download_raw_data()
create_dataset(output_path='data/OCW_0.2/', trim=True)


# create_dataset(data_source='data/data_source_intro_only.csv',
#                output_path='data/trimmed/',
#                force_aligned=False, trim=True)

# create_dataset(data_source='data/data_source_intro_only.csv',
#                output_path='data/aligned/',
#                force_aligned=True)
# print(strip_srt('data/raw/MIT5_07SCF13_JoAnne_Redox_300k.srt',
#           'data/raw/MIT5_07SCF13_JoAnne_Redox_300k.txt'))
# extract_audio('https://archive.org/download/MIT5.07SCF13/MIT5_07SCF13_JoAnne_Intro_300k.mp4')