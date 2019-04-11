import numpy as np     
import matplotlib.pyplot as plt     #import modules needed
import math
import time
from matplotlib.pyplot import scatter
import pylab
from matplotlib import animation
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
body_num=int(input('The number of bodies:'))
time_step=2000 #set time_step
max_step=10000 #set_iteration time
loc_his=list()   # store the location data for each step for display
start_time=time.time() #
mass=1e24*np.random.randint(low=1,high=100,size=body_num)#generate random masses for bodies from 10^24 to 10^29
location=1e9+1e9*np.random.rand(body_num,2) #generate two dimentional location with in range 10^9 to 2*10^9
velocity=np.zeros((body_num,2),dtype=float) #initial velocity which are all zero
acceleration=np.zeros((body_num,2),dtype=float) #initial acceleration which are all zero
G=6.67408e-11 #define the constant for universal gravitation constant
loc_his.append(location) #

'''
for specific body, calculated its join force 
and get the caululation 
'''
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

''' with time step and acceleration, update the velpcity'''
def update_velocity():
    global velocity, acceleration
    for i in range(body_num):
        calculate_acceleration(i)
    velocity=np.sum([velocity,time_step*acceleration],axis=0)
    acceleration=np.zeros((body_num,2),dtype=float)

''' for each time step update location with velocity'''
def update_location():
    global location, loc_his
    location=np.sum([location,time_step*velocity],axis=0)
    loc_his.append(location)

'''
check if the distance reach the limit, if yes turn the velocity to opposite direction
'''
def check_collision():
        for body_index in range(body_num):
                for index in range(body_index+1,body_num):
                        r2=sum(np.square(location[body_index]-location[index]))
                        if r2**(1/2)<1e-8:
                                velocity[index]=-velocity[index]
                                velocity[body_index]=-velocity[index]
def check_border():
        ''' check if a body is out of border, if yes redo the random initialization for it'''
        for i in range(body_num):
                if -3e9<location[i][0]<3e9 and -3e9<location[i][1]<3e9:
                        continue
                else: 
                        location[i]=1e9+1e9*np.random.rand(1,2)
                        velocity[i]=np.zeros((1,2),dtype=float)

'''repeat multiple times according to the limit setting'''
def simulation(max_step):
    for i in range(max_step):
        check_border()
        check_collision()
        update_velocity()
        update_location()
simulation(max_step)
end_time=time.time()



''' 
break the location history according to x and y axis for display
'''
x = np.random.random_sample((max_step,body_num))
y = np.random.random_sample((max_step,body_num))
for i in range(body_num):
        for j in range(max_step):
                x[j][i]=loc_his[j][i][0]
                y[j][i]=loc_his[j][i][1]
p = point(x,y)
print(end_time-start_time)
p()
