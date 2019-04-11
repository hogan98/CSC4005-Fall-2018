import numpy as np
import matplotlib.pyplot as plt
import time
x_size,y_size=800,800
ite_limit=100
def mandelbrot_set_ite(x,y,ite_limit):
    c=(x-400)/200+(y-400)/200*1j
    z=0+0j
    ite_time=0
    while abs(z)<2 and ite_time<ite_limit:
        z=z**2 +c
        ite_time+=1
    if ite_time==ite_limit:
        return 1
    else:
        return 0
pix_set= np.zeros([x_size, y_size], dtype='i')
start_time=time.time()
for j in range(x_size):
    for i in range(y_size):
        x = j
        y = i
        pix_set[i, j] = mandelbrot_set_ite(x, y, ite_limit)
end_time=time.time()
#print(end_time-start_time)
plt.xticks([])
plt.yticks([])
plt.imshow(pix_set,aspect='equal',cmap='gray_r')
plt.show()