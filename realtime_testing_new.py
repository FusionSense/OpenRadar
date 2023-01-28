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
IQ = 2
# ----------CHANGE num_frames TO WHAT WE USE-------------
num_frames = 1
# -------------------------------------------------------


#Makes the appropriate data structure for post processing
# Returns one frame of data 
def reorganize(adc):
    cube_ = adc.reshape(numRxAntennas, IQ, numADCSamples, numTxAntennas, numChirpsPerFrame//numTxAntennas, order='F')
    cube_ = np.moveaxis(cube_, [0,1,2,3,4], [2,0,4,1,3])
    cube = cube_[0] + 1j * cube_[1]
    return cube


def doppler(matrix, fast_time):
    fft_out = np.fft.fft2((matrix)*np.blackman(fast_time), axes=(0,2))            # 2D fft along slow time and fa st time
    rdm_log = np.log10(np.abs(fft_out)/2**15)           # normalizing the 16 bit number
    #print(rdm_log.shape)                                
    rdm = np.sum(rdm_log, axis=1)                       # averages the fft calculation along the virtual antenna axis \

    return np.fft.fftshift(rdm, axes=0)


dca = DCA1000()
times = []
while True:
    start = datetime.utcnow() # Start Timer
    adc_data = dca.read() # Read in ADC data from the DCA board

    # get radar cube data
    
    radar_cube = reorganize(adc_data, numTxAntennas, numRxAntennas, numChirpsPerFrame//numTxAntennas, numADCSamples)


    det_matrix_vis = doppler(radar_cube, numADCSamples)
    
    normalized = det_matrix_vis-det_matrix_vis.max()
    #end = datetime.utcnow()
    print(num_frames)
    num_frames = num_frames + 1


    # *************Start of Plotting**************
    plt.imshow(normalized.T, origin='lower', aspect='auto',vmin=-90)
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
    
    end = datetime.utcnow()
    times.append((end-start).microseconds)
    if num_frames == 100:
        #save_str = "{0}{1}.txt".format("adc_data",num_frames)
        #np.savetxt(save_str,adc_data)
        
        
        print(np.mean(times)/1e6)    