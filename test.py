import mmwave as mm
from mmwave.dataloader import DCA1000
import numpy as np 


dca = DCA1000()
adc_data = dca.read()
radar_cube = mm.dsp.range_processing(adc_data)


np.savetxt('adc_data.txt',adc_data)
np.savetxt('radar_cube.txt',radar_cube)
#print(adc_data)
#print(radar_cube)
