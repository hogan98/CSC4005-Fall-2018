from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
import math                             #import modules needed
import time
from matplotlib.pyplot import scatter
import pylab
from matplotlib import animation
time_step=2000 #set time_step
max_step=10000 #set_iteration time
G=6.67408e-11 #define the constant for universal gravitation constant

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


comm=MPI.COMM_WORLD #initialize the MPI enviroment
size=comm.Get_size()
rank=comm.Get_rank()



if rank==0:
        body_num=int(input('The number of bodies:'))
        mass=1e24*np.random.randint(low=1,high=100,size=body_num)#generate random masses for bodies from 10^24 to 10^29
        location=1e9+1e9*np.random.rand(body_num,2) #generate two dimentional location with in range 10^9 to 2*10^9
        comm.bcast(body_num,root=0) #send number of bodier to each processss
        loc_his=list() #
        loc_his.append(location)
        comm.barrier() #make sure above operation in rank 0 before other process
else:
        comm.barrier() # stop all pther
        location,mass=None,None
        body_num=comm.bcast(None,root=0)
velocity=np.zeros((body_num,2),dtype=float) #initial velocity which are all zero
#for column 67 to 71, get the number of bodies assigned to each process
sub_body_num=[body_num//size for _ in range(size)] 
for k in range(size):
    sub_body_num[k]=sub_body_num[k]+(body_num%size>k)  
body_range=[0]+list(np.cumsum(sub_body_num))





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
def update_location():
    global movement
    movement=np.sum([location,time_step*velocity],axis=0)-location
def check_collision(l):
        for body_index in range(l[0],l[1]):
                for index in range(body_index+1,body_num):
                        r2=sum(np.square(location[body_index]-location[index]))
                        if r2**(1/2)<1e-8:
                                velocity[index]=-velocity[index]
                                velocity[body_index]=-velocity[index]
def check_border(l):
        for i in range(l[0],l[1]):
                #print(i,rank)
                #print(location[i],111,rank)
                #print(location[i][0],222,rank)
                if -3e9<location[i][0]<3e9 and -3e9<location[i][1]<3e9:
                        pass
                else: 
                        location[i]=1e9+1e9*np.random.rand(1,2)
                        velocity[i]=np.zeros((1,2),dtype=float)
def simulation(a,b): #do simulation only to the assgned body for each process
    l=[a,b]
    check_border(l)
    check_collision(l)
    update_velocity(l)
    update_location()


start_time=time.time()

for i in range(max_step):
        location=comm.bcast(location,root=0)
        mass=comm.bcast(mass,root=0)
        acceleration=np.zeros((body_num,2),dtype=float)
        simulation(body_range[rank],body_range[rank+1])
        comm.send(movement,dest=0)#send the movement of each body to rank 0 process 
        comm.barrier()#make sure each process do not repeat simulation until location data is updated
        '''
        after each process simulate one time, 
        gather the information and unpate location for next simulation
        '''
        if rank==0: 
                movement=np.zeros((body_num,2),dtype=float)
                for j in range(size):
                        par_move=comm.recv(source=j)
                        movement=movement+par_move
                location=location+movement
                loc_his.append(location) # store the location data
end_time=time.time()
if rank==0: #display the oribt
        x = np.random.random_sample((max_step,body_num))
        y = np.random.random_sample((max_step,body_num))
        for i in range(body_num):
                for j in range(max_step):
                        x[j][i]=loc_his[j][i][0]
                        y[j][i]=loc_his[j][i][1]
        p = point(x,y)
        p()
