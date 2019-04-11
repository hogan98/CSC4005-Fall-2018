import matplotlib.pyplot as plt
import numpy as np
import time
x_size,y_size=800,800 # set size for different axes
ite_limit=100 #set limit for iteration time
numThr = int(input('number of threads:')) # number of threads to run
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
def thread_man(k):
    pix_set=np.zeros([sub_list[k],y_size],dtype='i')
    # each thread only calculates its own share of pixels
    for i in range(sum(sub_list[0:k]),sum(sub_list[0:k])+sub_list[k]):
        for j in range(800):
            x=i
            y=j
            pix_set[i-sum(sub_list[0:k]),j]= mandelbrot_set_ite(x, y, ite_limit)
    return pix_set

if __name__ == "__main__":
    from multiprocessing.dummy import Pool as mp
    start_time=time.time()
    #get the number of columns for each column
    sub_list=[800//numThr for _ in range(numThr)]
    for k in range(numThr):
        sub_list[k]=sub_list[k]+(800%numThr>k)
    #intialize the process pool
    pool=mp(numThr)
    #gather the result from each thread
    all_result=pool.map(thread_man,list(range(numThr)))
    #formalize the result for output
    count=1
    fin_res=all_result[0]
    while count < numThr:
        fin_res=np.vstack((fin_res,all_result[count]),)
        count+=1
    pool.close()
    pool.join()
    end_time=time.time()
    #print(end_time-start_time)
    #output the plot with matplotlib
    plt.xticks([])
    plt.yticks([])
    plt.imshow(fin_res.T,aspect='equal',cmap='gray_r')
    plt.show()