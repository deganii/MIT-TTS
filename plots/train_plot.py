import numpy as np
import os
import matplotlib
import re

matplotlib.use('Agg')
import matplotlib.pyplot as plt

class FitPlotter(object):
    @classmethod
    def save_plot(cls, path=None, title=''):
        # plot and save to disk
        train_loss = [re.findall(r'Train loss (\d+) (\d+\.\d+) .*', line)
            for line in open(path)]
        val_loss = [re.findall(r'Validation loss (\d+):  (\d+\.\d+) .*', line)
            for line in open(path)]

        np_train = np.array([np.array(xi)
            for xi in train_loss if len(xi) > 0])
        np_train = np.concatenate(np_train).astype(np.float)

        np_val = np.array([np.array(xi)
            for xi in val_loss if len(xi) > 0])
        np_val = np.concatenate(np_val).astype(np.float)


        fig = plt.figure(figsize=(4,2))
        #title = "Learning Rate"
        fig.suptitle('', fontsize=10, fontweight='bold')
        ax = fig.add_subplot(111)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')

        # iterations per epoch
        it_per_epoch = 33.0

        ax.plot(np_train[:,0]/it_per_epoch, np_train[:,1],
                label='Train', linewidth=0.5)
        ax.plot(np_val[:,0]/it_per_epoch, np_val[:,1],
                label='Validation', linewidth=1.5)
        ax.annotate('Optimal (~ Epoch 31)', xy=(40., .3), xytext=(100, 1.5),
                    arrowprops=dict(facecolor='gray', color='gray', shrink=0.05),
                    )
        # plt.axvline(x=1000.0/33., color='gray',
        #             linewidth=1.,
        #         linestyle='--', ymin=0.2, ymax=0.8)
        ax.legend()
        fig.subplots_adjust(left = 0.24)
        fig.subplots_adjust(bottom = 0.27)
        fig.subplots_adjust(right = 0.96)
        fig.subplots_adjust(top = 0.94)
        fig.canvas.draw()
        #plt.show()

        plt.savefig(path + '.png')
        plt.close(fig)

# Test case
FitPlotter.save_plot(title="Freeze_decoder",
    path = "../logs/ocw0.2.train.log")