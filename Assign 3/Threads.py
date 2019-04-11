import numpy as np
import matplotlib.pyplot as plt
import math                     #import modules needed
import time
from matplotlib.pyplot import scatter
import pylab
from matplotlib import animation
import threading
body_num=int(input('The number of bodies:'))
numThr=int(input('The number of threads:'))
time_step=2000#set time_step
max_step=10000#set_iteration time
loc_his=list()
start_time=time.time()
mass=1e24*np.random.randint(low=1,high=100,size=body_num)#generate random masses for bodies from 0 to 10
location=1e9+1e9*np.random.rand(body_num,2) #generate two dimentional location with in range 0 to 1
velocity=np.zeros((body_num,2),dtype=float) #initial velocity which are all zero
acceleration=np.zeros((body_num,2),dtype=float)
movement=np.zeros((body_num,2),dtype=float)
G=6.67408e-11 #define the constant for universal gravitation constant
loc_his.append(location)

class point: # define a class in python for the orbit display
    def __init__(self,x=None,y=None):
        # create plot, which contain two subplots
        self.fig = plt.figure(figsize=(15, 10))
        self.ax = self.fig.add_subplot(1, 1, 1)
        plt.xlim(-5e9,5e9) # set display region
        plt.ylim(-5e9,5e9) # set display region
        #plt.xticks([])
        #plt.yticks([])
        self.frame = max_step
        self.x1, self.y1 = x, y
        self.sca = (self.ax).scatter(self.x1, self.y1)
    def init(self):
        data = [[x,y] for x,y in zip((self.x1)[0],(self.y1)[0])]
        (self.sca).set_offsets(data)  # scatter plot
        label = 'timestep {0}'.format(0)
        (self.ax).set_xlabel(label)
        return self.sca,self.ax
    def animate(self,i):
        x1, y1 = (self.x1)[i], (self.y1)[i]
        data = [[x,y] for x,y in zip(x1,y1)]
        self.sca.set_offsets(data)  # scatter plot
        label = 'timestep {0}'.format(i)
        (self.ax).set_xlabel(label)
        return self.sca,self.ax
    def __call__(self): #use animation.FunAnimation to display the dynamic scatter plot
        ani = animation.FuncAnimation(fig=self.fig,
                                      func=self.animate,
                                      frames=self.frame,
                                      init_func=self.init,
                                      interval=100,
                                      blit=False)
        plt.show()

def calculate_acceleration(body_index):
    temp_a=[0,0]
    for index in range(body_num):
        if index != body_index:
            r2=sum(np.square(location[body_index]-location[index]))
            r=math.sqrt(r2)
            a=G*mass[index]/r2
            a_component=[a*(location[index][0]-location[body_index][0])/r,a*(location[index][1]-location[body_index][1])/r]
            #print(a_component,body_index)
            temp_a=np.sum([a_component,temp_a],axis=0)
    acceleration[body_index]=temp_a
def update_velocity(l):
    global velocity, acceleration
    for i in range(l[0],l[1]):
        calculate_acceleration(i)
    velocity=np.sum([velocity,time_step*acceleration],axis=0)
    acceleration=np.zeros((body_num,2),dtype=float)
def check_collision(l):
        for body_index in range(l[0],l[1]):
                for index in range(body_index+1,body_num):
                        r2=sum(np.square(location[body_index]-location[index]))
                        if r2**(1/2)<1e-8:
                                velocity[index]=-velocity[index]
                                velocity[body_index]=-velocity[index]
def check_border(l):
        for i in range(l[0],l[1]):
                if -3e9<location[i][0]<3e9 and -3e9<location[i][1]<3e9:
                        continue
                else: 
                        location[i]=1e9+1e9*np.random.rand(1,2)
                        velocity[i]=np.zeros((1,2),dtype=float)

def update_location(l):
    for i in range(l[0],l[1]):
        movement[i][0]=(time_step*velocity)[i][0]
        movement[i][1]=(time_step*velocity)[i][1]

def simulation(a,b):
    global location
    l=[a,b]
    for i in range(max_step):
        check_border(l)
        check_collision(l)
        update_velocity(l)
        update_location(l)
        threading.Barrier(body_num)
        if threading.current_thread().name=='Thread-1':
            location=location+movement
            loc_his.append(location)
if __name__ == "__main__":

    start_time=time.time()
    #for column 111 to 114, get the number of bodies assigned to each process
    sub_num=[body_num//numThr for _ in range(numThr)]
    for k in range(numThr):
        sub_num[k]=sub_num[k]+(body_num%numThr>k)  
    sub_list=[0]+list(np.cumsum(sub_num))
    threads=[]
    lock = threading.Lock()
    for j in range(numThr):
        t=threading.Thread(target=simulation,args=([sub_list[j],sub_list[j+1]]))
        threads.append(t)
    for j in range(numThr):
        threads[j].start()
    for j in range(numThr):
        threads[j].join()
    end_time=time.time()
    x = np.random.random_sample((max_step,body_num))
    y = np.random.random_sample((max_step,body_num))
    for i in range(body_num):
        for j in range(max_step):
                x[j][i]=loc_his[j][i][0]
                y[j][i]=loc_his[j][i][1]
    p = point(x,y)
    p()
 