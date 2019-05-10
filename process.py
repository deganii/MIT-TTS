
import srt
import os
from pydub import AudioSegment
import csv
import subprocess
import urllib.request

def path_from_url(url):
  return 'data/raw/' + url.rsplit('/', 1)[1]

def download_audio(video_url, save_path=None,
                  sample_rate=22050, channels=1):
  if save_path is None:
    save_path = path_from_url(video_url)
  audio_path = save_path + '.wav'
  urllib.request.urlretrieve(video_url, save_path)
  # -f s16le
  command = "ffmpeg -i {0} -ar {1} -ac {2} -vn {3}"\
    .format(save_path, sample_rate, channels, audio_path)
  subprocess.call(command, shell=True)
  os.remove(save_path)
  return audio_path

def download_srt(srt_url, save_path=None):
  if save_path is None:
    save_path = path_from_url(srt_url)
  urllib.request.urlretrieve(srt_url, save_path)

# strips the SRT file to just plain text fragments
# useful for finding out the
def strip_srt(srt_path, save_path=None):
  with open(srt_path, 'r') as myfile:
    data = myfile.read()
  content_only = [sd.content for sd in srt.parse(data)]
  if save_path is not None:
    with open(save_path, 'w') as save_file:
      save_file.writelines(content_only)
  return content_only

# use aeneas to align audio automagically
# def align_audio(text_path, audio_path):
  # import aeneas
  # aeneas.tools.execute_task

def download_raw_data():
  with open('data/data_sources.csv', 'r') as ds_file:
    csv_reader = csv.reader(ds_file, delimiter=',')
    next(csv_reader)  # skip the header
    # read the names in data sources
    for name, video, srt in csv_reader:
      download_audio(video, "data/raw/{0}.wav".format(name))
      download_srt(srt, "data/raw/{0}.srt".format(name))

def align_raw_data():
  with open('data/data_sources.csv', 'r') as ds_file:
    csv_reader = csv.reader(ds_file, delimiter=',')
    next(csv_reader)  # skip the header
    # read the names in data sources
    for name, video, srt in csv_reader:
      audio_path = "data/raw/{0}.wav".format(name)
      srt_path = "data/raw/{0}.srt".format(name)
      text_path = "data/raw/{0}.txt".format(name)
      output_path = "data/raw/{0}.realigned.srt".format(name)
      strip_srt(srt_path, save_path=text_path)
      force_align_audio(audio_path, text_path, output_path)

# align text using aeneas package
def force_align_audio(audio_path, text_path, output_path):
  from aeneas.exacttiming import TimeValue
  from aeneas.executetask import ExecuteTask
  from aeneas.language import Language
  from aeneas.syncmap import SyncMapFormat
  from aeneas.task import Task
  from aeneas.task import TaskConfiguration
  from aeneas.textfile import TextFileFormat
  import aeneas.globalconstants as gc

  # create Task object
  config = TaskConfiguration()
  config[gc.PPN_TASK_LANGUAGE] = Language.ENG
  config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
  config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.SRT
  task = Task()
  task.configuration = config
  task.audio_file_path_absolute = audio_path
  task.text_file_path_absolute = text_path
  task.sync_map_file_path_absolute = output_path
  ExecuteTask(task).execute()
  # print(task.sync_map)

# create a dataset from a list of srt/audio pairs
def create_dataset():
  if(os.path.exists('data/wavs')):
    os.remove('data/wavs')
  os.makedirs('data/wavs', exist_ok=True)

  # split up the wav files, and create a metadata.csv
  with open('data/metadata.csv', 'w', newline='') as meta_file:
    csvwriter = csv.writer(meta_file, delimiter='|',
      quotechar='"', quoting=csv.QUOTE_MINIMAL)
    counter = 0
    with open('data/data_sources.csv', 'r') as ds_file:
      csv_reader = csv.reader(ds_file, delimiter=',')
      next(csv_reader) # skip the header
      # read the names in data sources
      for name, video, srt in csv_reader:
        srt_path = "data/raw/{0}.srt".format(name)
        audio_path = "data/raw/{0}.wav".format(name)
        text_path = "data/raw/{0}.txt".format(name)

        strip_srt(srt_path, text_path)

        with open(srt_path, 'r') as srt_file:
          data = srt_file.read()
        srt_data = list(srt.parse(data))
        wfile = AudioSegment.from_wav(audio_path)

        for sd in srt_data:
          id = "{0:04d}-{1}".format(counter, name)
          content = sd.content.replace('\n', ' ').replace('\r', '')
          st = int(sd.start.total_seconds() * 1000)
          end = int(sd.end.total_seconds() * 1000)
          clip = wfile[st:end]
          clip.export("data/wavs/{0}.wav".format(id), format="wav")
          # put an extra column in case we need to adjust the text
          csvwriter.writerow([id, content, content])
          counter = counter+1




#create_dataset()

# print(strip_srt('data/raw/MIT5_07SCF13_JoAnne_Redox_300k.srt',
#           'data/raw/MIT5_07SCF13_JoAnne_Redox_300k.txt'))
# extract_audio('https://archive.org/download/MIT5.07SCF13/MIT5_07SCF13_JoAnne_Intro_300k.mp4')