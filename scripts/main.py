#!/usr/bin/env python
import csv

import time
import rospy
import sys
import numpy as np
from std_msgs.msg import Float32
from std_msgs.msg import Empty as EmptyMsg
from std_msgs.msg import Int32
from ratio_consensus.msg import ratio_consensus_msg as Msg
from ratio_consensus.msg import all_info as AllInfoMsg
import copy

rospy.init_node('Slave', anonymous=True)

val=[]
m=9.0
STEP_SIZE=.1

if rospy.has_param("/dataset"):
  dataset_filename=rospy.get_param("/dataset")
else:
  print("Set data_set name")
  exit()

with open(dataset_filename) as csv_file:

  csv_reader = csv.reader(csv_file, delimiter=',')
  line_count = 0
  for row in csv_reader:
      val.append(float(row[0]))
      line_count+=1
  max_iter=line_count

def cap(val,low,high):
  if val < low:
    return low
  if val>high:
    return high
  return val

class Slave:
	def __init__(self):
            if rospy.has_param("~ident"):
                self.ident = int(rospy.get_param("~ident"))
                # print(self.ident)
            else:
                print "Identity of this computer is not set. Exiting"
                exit()
            self.f=open('/home/aaron/catkin_ws/src/ratio_consensus/scripts/'+str(self.ident)+".csv","w")

            with open('/home/aaron/catkin_ws/src/ratio_consensus/gu.csv') as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=',')
              for row in csv_reader:
                 self.gu=(float(row[self.ident]))


            self.one_hop_neighbors=[]
            with open('/home/aaron/catkin_ws/src/ratio_consensus/go.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    self.go=(float(row[self.ident]))

            self.two_hop_neighbors=[]
            self.three_hop_neighbors=[]
            for i in range(100):
                try:
                    s=rospy.get_param("~incoming"+str(i))
                    self.one_hop_neighbors.append(int(s))
                except:
                    pass
                try:
                    s=rospy.get_param("~2incoming"+str(i))
                    self.two_hop_neighbors.append(int(s))
                except:
                    pass
                try:
                    s=rospy.get_param("~3incoming"+str(i))
                    self.three_hop_neighbors.append(int(s))
                except:
                    pass

            rospy.Subscriber('/outer_loop', Int32, self.outerLoopCB)
            self.ack_pub=rospy.Publisher('/'+str(self.ident)+'/ack', Msg, queue_size=10)
            rospy.Subscriber('/all_info', AllInfoMsg, self.allInfoCB)
            self.state=Msg()
            self.state.id=int(self.ident)
            if self.ident==0:
              self.state.y=val[0]-self.gu
            else:
              self.state.y=-self.gu
            self.state.z=self.go-self.gu

        def outerLoopCB(self,msg):
            self.f.write(str(self.state.P)+"\n")
            self.iteration2=msg.data
            self.update_y()

        def allInfoCB(self,msg):
            '''
            Starting of a round.  Do some calculations, set val_msg and then send out to neighbors
            '''
            self.update(msg)
            self.pub()

        def pub(self):
          self.ack_pub.publish(self.state)


        def update(self,msg):
          z_sum=0.0
          y_sum=0.0
          for neighbor in self.one_hop_neighbors:
              y_sum+=msg.y[neighbor]
              z_sum+=msg.z[neighbor]
          self.state.y=1./3.*(self.state.y+y_sum)
          self.state.z=1./3.*(self.state.P+z_sum)
          self.state.time=msg.time+1
          self.state.P=self.gu+(self.y/self.z)*(self.go-self.gu)


        def update_y(self):
          if self.ident==0:
            self.state.y=val[self.iteration2]-self.gu
          else:
            self.state.y=-self.gu
          self.state.z=self.go-self.gu

        def run(self):
            while not rospy.is_shutdown():
              # self.pub()
              time.sleep(.1)

def main(args):
	manager=Slave()
	try:
		manager.run()
	except KeyboardInterrupt:
		print("Draw: Shutting down")

if __name__ == '__main__':
	main(sys.argv)
