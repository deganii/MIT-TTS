import numpy as np
import os
import csv

# partition data into train/test/validation
# post-process into "filelist" required by NVIDIA tacotron2 implementation
DS_VERSION = "0.2"

# by default, 60% goes to train, 20% to test and validation sets
train_pct = 0.7
val_pct = 0.2

def save_set(path, data, indices):
    with open(path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='|',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in indices:
            csvwriter.writerow([data[i][0], data[i][2]])


def build_filelist(ds_path):
    with open(ds_path + 'metadata.csv', 'r') as meta_file:
        reader = csv.reader(meta_file, delimiter='|')
        data = list(list(rec) for rec in reader)
        wav_path = ds_path + "wavs"
        # replace the id with the path of the wave file
        for i in range(len(data)):
            data[i][0] = "{0}/{1}.wav".format(wav_path, data[i][0])

    np.random.seed(0)
    indices = np.random.permutation(len(data))
    train = int(np.floor(train_pct * len(data)))
    val = int(np.floor((train_pct+val_pct) * len(data)))
    train_idx = indices[:train]
    val_idx = indices[train:val]
    test_idx = indices[val:]

    partition_path = ds_path+'filelists'
    os.makedirs(partition_path, exist_ok=True)
    save_set('{0}/ocw_train.txt'.format(partition_path), data, train_idx)
    save_set('{0}/ocw_val.txt'.format(partition_path), data, val_idx)
    save_set('{0}/ocw_test.txt'.format(partition_path), data, test_idx)

# build_filelist('/home/ubuntu/OCW_{0}/wavs'.format(DS_VERSION)
build_filelist('/home/ubuntu/MIT-TTS/data/OCW_{0}/'.format(DS_VERSION))
l
