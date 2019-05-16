from aeneas.exacttiming import TimeValue
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc
import csv
import srt
import os

# Programmatically run aeneas. Similar to the command line:
# python3.6 -m aeneas.tools.execute_task [AUDIO] [TEXT] [CONFIG] [OUTPUT]
# CONFIG: "task_language=eng|is_text_type=plain|os_task_file_format=srt"


# strips the SRT file to just plain text fragments
# useful for finding out the
def strip_srt(srt_path, save_path=None):
  with open(srt_path, 'r') as myfile:
    data = myfile.read()
  content_only = [sd.content.replace('\n', ' ') + "\n\n"
                  for sd in srt.parse(data)]
  if save_path is not None:
    with open(save_path, 'w') as save_file:
      save_file.writelines(content_only)
  return content_only

def align_raw_data():
  os.makedirs("data/raw", exists_ok=True)
  with open('data/data_sources.csv', 'r') as ds_file:
    csv_reader = csv.reader(ds_file, delimiter=',')
    next(csv_reader)  # skip the header
    # read the names in data sources
    for name, video, srt in csv_reader:
      audio_path = "data/raw/{0}.wav".format(name)
      srt_path = "data/raw/{0}.srt".format(name)
      text_path = "data/raw/{0}.txt".format(name)
      output_path = "data/raw/{0}.realigned.srt".format(name)
      #strip_srt(srt_path, save_path=text_path)
      force_align_audio(audio_path, text_path, output_path)

# align text using aeneas package
def force_align_audio(audio_path, text_path, output_path):
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



strip_srt("data/raw/MIT5_07SCF13_JoAnne_Intro.srt",
           save_path="data/raw/MIT5_07SCF13_JoAnne_Intro2.txt")
# force_align_audio("/home/ubuntu/MIT-TTS/data/raw/MIT5_07SCF13_JoAnne_Intro.wav",
#                  "/home/ubuntu/MIT-TTS/data/raw/MIT5_07SCF13_JoAnne_Intro.txt",
#                   "/home/ubuntu/MIT-TTS/data/raw/MIT5_07SCF13_JoAnne_Intro.aligned.srt")
