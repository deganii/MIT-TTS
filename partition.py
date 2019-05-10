import numpy as np
import os
import csv

# partition data into train/test/validation
# post-process into "filelist" required by NVIDIA tacotron2 implementation
DS_VERSION = "0.2"

# by default, 60% goes to train, 20% to test and validation sets
train_pct = 0.6
val_pct = 0.2

def save_set(path, data, indices):
    with open(path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='|',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in indices:
            csvwriter.writerow([data[i][0], data[i][2]])

def build_filelist(wav_path):
    with open('data/metadata.csv', 'r') as meta_file:
        reader = csv.reader(meta_file, delimiter='|')
        data = list(list(rec) for rec in reader)
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

    os.makedirs('filelists', exist_ok=True)
    save_set('filelists/ocw_train.txt', data, train_idx)
    save_set('filelists/ocw_val.txt', data, val_idx)
    save_set('filelists/ocw_test.txt', data, test_idx)

# build_filelist('/home/ubuntu/OCW_{0}/wavs'.format(DS_VERSION)