import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import mmwave as mm
import mmwave.dsp as dsp
import numpy as np
from mmwave.dataloader import DCA1000
from mmwave.dsp.utils import Window
from datetime import datetime

numChirpsPerFrame = 192
numRxAntennas = 4
numADCSamples = 512
numTxAntennas = 3
IQ = 2
# ----------CHANGE num_frames TO WHAT WE USE-------------
num_frames = 1
# -------------------------------------------------------
dca = DCA1000()
times = []


# This is the radarcube(adc) function from Owens test script
# Renaming to reorganize for consistency  
def reorganize(adc):
    cube_ = adc.reshape(numRxAntennas, IQ, numADCSamples, numTxAntennas, numChirpsPerFrame//numTxAntennas, order='F')
    cube_ = np.moveaxis(cube_, [0,1,2,3,4], [2,0,4,1,3])
    cube = cube_[0] + 1j * cube_[1]
    return cube


def rangedoppler(cube, numADCSamples = 512):
    cube_ = cube * np.blackman(numADCSamples)[None,:]
    cube_ = cube_.squeeze()
    rdm = np.fft.fft2(cube_, axes=(0,1))
    rdm = np.fft.fftshift(rdm, axes=(0))

    ## log & normalize data to 0dB max
    return rdm

def normalize(rdm):
    global SCENE_MAX
    rdm=np.log2(np.abs(rdm))
    rdm=rdm-SCENE_MAX
    return rdm.T

# def visualize(rdm):
#     plt.imshow(np.abs(rdm.T), origin='lower', aspect='auto')
#     range_res = 0.05
#     vel_res = 1
#     range_step = 50
#     vel_step = 8
#     rangeAxis = np.arange(0,512,range_step)*range_res
#     velocityAxis = np.arange(-64/2,64/2,vel_step)*vel_res
#     plt.yticks(np.arange(0,512,range_step),rangeAxis)
#     plt.xticks(np.arange(0,64,vel_step),velocityAxis)
#     plt.title(label=num_frames-1)
#     plt.colorbar()
#     plt.show()
#     return rdm

def generate_data():
    adc_data = dca.read() # Read in ADC data from the DCA board
    radar_cube = reorganize(adc_data)
    frame = radar_cube[0][0]
    newrdm = normalize(rangedoppler(frame)) # generate data
    return newrdm


def update(data):
    mat.set_data(data)
    
    return mat

def data_gen():
    global start
    while True:
        new=datetime.utcnow()
        print(new-start)
        start=new
        yield generate_data()



start = datetime.utcnow() # Start Timer

fig, ax = plt.subplots()
adc_data = dca.read() # Read in ADC data from the DCA board
radar_cube = reorganize(adc_data)
frame = radar_cube[0][0]
data_0 = rangedoppler(frame) # generate data
data_0=np.log2(np.abs(data_0))
SCENE_MAX=np.max(data_0)
data_0=(data_0-SCENE_MAX).T


mat = ax.imshow(data_0, origin = "lower", interpolation="nearest", vmin=-17, vmax=0)
plt.colorbar(mat)
ax.set_aspect('auto')
ani = animation.FuncAnimation(fig, update, data_gen, interval = 0)
plt.show()
print(num_frames)
num_frames = num_frames + 1
end = datetime.utcnow()


times.append((end-start).microseconds)
if num_frames == 100:
    #save_str = "{0}{1}.txt".format("adc_data",num_frames)
    #np.savetxt(save_str,adc_data)
    
    
    print(np.mean(times)/1e6)    