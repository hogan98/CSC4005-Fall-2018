import numpy as np
from mpi4py import MPI
import time
x_size,y_size=800,800 # set size for different axes
ite_limit=100 #set limit for iteration time
def mandelbrot_set_ite(x,y,ite_limit): #check if the point is converge
    c=(x-400)/200+(y-400)/200*1j #scale factor for the points
    z=0+0j # original point
    ite_time=0
    while abs(z)<2 and ite_time<ite_limit: # use while-loop to check convergence
        z=z**2 +c
        ite_time+=1
    if ite_time==ite_limit:
        return 1 #return 1 for converge points
    else:
        return 0 #return 0 for diverge points
comm=MPI.COMM_WORLD #initialize the MPI enviroment
size=comm.Get_size()
rank=comm.Get_rank()
if rank==0:
    start_time=time.time()
col_num=x_size//size+(x_size%size>rank) #sperate sub area for each process to compute by seperating the x axis
sub_col=(comm.scan(col_num)-col_num,comm.scan(col_num))# the sub x axis range for each process

pix_set=np.zeros([col_num,y_size],dtype='i') #define a array to store the sub result
for j in range(y_size): # do the iteration for the points in the subarea and store them to pix_set
    for i in range(sub_col[0],sub_col[1]):
        x = i
        y = j
        pix_set[i-sub_col[0], j] = mandelbrot_set_ite(x, y, ite_limit)

counts=comm.gather(col_num,root=0)# number of points in each subarea
sub_result=None 
if rank==0:
    sub_result=np.zeros([x_size,y_size],dtype='i') #define arrray to gather the final reult to process 0

rowtype = MPI.INT.Create_contiguous(x_size)
rowtype.Commit()
comm.Gatherv(sendbuf=[pix_set, MPI.INT],  #use Gatherv to get the final result to process 0
recvbuf=[sub_result, (counts, None), rowtype],
root=0)
rowtype.Free()

end_time=time.time()

if rank==0:
    #print(end_time-start_time)
    import matplotlib.pyplot as plt # use module matplotlib to display the final result
    plt.xticks([])
    plt.yticks([])
    plt.imshow(sub_result.T,aspect='equal',cmap='gray_r')
    plt.show()
