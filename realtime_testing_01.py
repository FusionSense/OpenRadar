import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
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
# ----------CHANGE num_frames TO WHAT WE USE-------------
num_frames = 1
# -------------------------------------------------------


#Makes the appropriate data structure for post processing
# Returns one frame of data 
def reorganize(adc,tx,rx,slow_time,fast_time):
    adc = adc.reshape(slow_time*tx, fast_time, 2, rx)   # actual data from DCA board being reshaped into stacked I,Q data 
    adc = adc[:,:,0,:]+1j*adc[:,:,1,:]                  # indec 0 calls the I's --> index 1 calls the Q's --> then combines each IQ pair
    adc=adc.swapaxes(1,2)                               # get data ready for reshape
    matrix = adc.reshape(slow_time,rx*tx,fast_time)     # reshapes the data into (num_chirps_per_transmitter, num_virtual_antennas, num_samples)
    return matrix


def doppler(matrix, fast_time):
    fft_out = np.fft.fft2((matrix)*np.blackman(fast_time), axes=(0,2))            # 2D fft along slow time and fa st time
    rdm_log = np.log10(np.abs(fft_out)/2**15)           # normalizing the 16 bit number
    #print(rdm_log.shape)                                
    rdm = np.sum(rdm_log, axis=1)                       # averages the fft calculation along the virtual antenna axis 

    return np.fft.fftshift(rdm, axes=0)


dca = DCA1000()
times = []
while True:
    
    adc_data = dca.read() # Read in ADC data from the DCA board

    # get radar cube data
    start = datetime.utcnow() # Start Timer
    radar_cube = reorganize(adc_data, numTxAntennas, numRxAntennas, numChirpsPerFrame//numTxAntennas, numADCSamples)


    det_matrix_vis = doppler(radar_cube, numADCSamples)
    
    normalized = (det_matrix_vis-det_matrix_vis.max()).T
    end = datetime.utcnow()
    print(num_frames)
    num_frames = num_frames + 1


    # *************Start of Plotting**************
    plt.imshow(normalized, origin='lower', aspect='auto',vmin=-50)
    range_res = 0.05
    vel_res = 1

    range_step = 50
    vel_step = 8

    rangeAxis = np.arange(0,512,range_step)*range_res
    velocityAxis = np.arange(-64/2,64/2,vel_step)*vel_res
    
    plt.yticks(np.arange(0,512,range_step),rangeAxis)
    plt.xticks(np.arange(0,64,vel_step),velocityAxis)
    #plt.xlabel(labelpad='Velocity (m/s)')
    #plt.ylabel(labelpad='Distance (m)')
    plt.title(label=num_frames-1)
    plt.colorbar()
    #plt.show()
    plt.pause(0.00001)
    #plt.savefig(f'temp{num_frames-1}.png')
    plt.clf()

    # ************

    # plt.savefig(f'temp{i}.png')
    
    times.append((end-start).microseconds)
    if num_frames == 100:
        print(np.mean(times)/1e6)    