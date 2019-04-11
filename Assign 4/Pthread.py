import numpy as np
import time
import matplotlib.pylab as plt
import threading

fire_temp=100   # temperature for fire
wall_temp=20    # temperature for wall
precision=1e-6
num=100

#create a list to store the temperature each iteration
temp_his=[]



'''
decide how many rows for each thread
'''
thread_num=int(input('num of threads: '))
sub_rows=[(num-2)//thread_num for _ in range(thread_num)]
for i in range(thread_num):
    sub_rows[i]=sub_rows[i]+((num-2)%thread_num>i)
sub_rows_range=[1]+sub_rows
sub_rows_range=list(np.cumsum(sub_rows_range))


'''
set function to display the distribution
'''
def heat_plot():
    check_r()
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    c = ax.pcolormesh(temp_his[len(temp_his) - 1], cmap='Spectral_r')
    plt.axis('off')
    cb = fig.colorbar(c)
    cb.set_label('Temperature')
    plt.show()



'''
define a function which will return 100x100 array where the wall and fire are
set with 20 and 100, while all others are 0
'''
def set_room(wall_temp,fire_temp,num):
    room = np.zeros((num, num))  # initialize the room with 100x100 array
    room[0], room[num - 1] = wall_temp + room[0], wall_temp + room[num - 1]
    for i in range(num):
        room[i][0],room[i][num-1]=wall_temp,wall_temp
    for i in range(int(.3*num),int(.70*num)):
        room[num-1][i]=fire_temp
    return(room)


#set the initial room and store it into list
initial_room=set_room(wall_temp,fire_temp,num)
temp_his.append(initial_room)


'''
check the change in temperature between two iteration, if all
changes for 100x100 points are less than precision, return True
'''
def check_precision():
    diff=temp_his[len(temp_his)-1]-temp_his[len(temp_his)-2]
    if ((diff>-precision).all()&(diff<precision).all())==True:
        return True
    else:
        return False



'''
when iteration stops, use check_r() such that all the data are set according to 5 degree
interval for plot, i.e a=5*x+c will be reset to a 
'''
def check_r():
    temp_room=temp_his[len(temp_his)-1]
    for i in range(num):
        for j in range(num):
            temp_room[i][j]=int((temp_room[i][j])/5)*5



#initial lock for multiple thread
lock = threading.Lock()




'''
perform jacobi iteration based on the data from last iteration,the input are the serial number of
rows for each thread
'''
def jacobi(lower,upper):
    global new_room,temp_his
    tag=True
    while tag==True:
        room=temp_his[len(temp_his)-1]
        for i in range(lower,upper):
            for j in range(1,num-1):
                new_room[i][j]=0.25*(room[i-1][j]+room[i+1][j]+room[i][j-1]+room[i][j+1])
        lock.acquire()
        if threading.current_thread().name == 'main':
            temp_his.append(new_room+initial_room)
        result = check_precision()
        if result==True:
            tag=False
        lock.release()






if __name__=='__main__':
    threads=[]
    a = threading.Thread(target=jacobi, args=([sub_rows_range[0], sub_rows_range[1]]), name='main')
    threads.append(a)
    for j in range(1, thread_num):
        t = threading.Thread(target=jacobi, args=([sub_rows_range[j], sub_rows_range[j + 1]]))
        threads.append(t)
    new_room = np.zeros((100, 100))
    start_time=time.time()
    for j in range(thread_num):
        threads[j].start()
    for j in range(thread_num):
        threads[j].join()
    heat_plot()