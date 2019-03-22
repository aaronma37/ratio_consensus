#!/usr/bin/env python

import csv
import time
import rospy
import sys
import random
from copy import deepcopy

from std_msgs.msg import Float32
from std_msgs.msg import Int32
from std_msgs.msg import Empty as EmptyMsg
from ratio_consensus.msg import all_info as AllInfoMsg
from ratio_consensus.msg import ratio_consensus_msg as RTOMsg

rospy.init_node('Master', anonymous=True)
all_info_pub=rospy.Publisher('/all_info', AllInfoMsg, queue_size=1)
outer_loop_pub =rospy.Publisher('/outer_loop', Int32, queue_size=1)

val=[]

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


gu=[]
go=[]

with open('/home/aaron/catkin_ws/src/ratio_consensus/gu.csv') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  for row in csv_reader:
    for i in range(9):
      gu.append(float(row[i]))
with open('/home/aaron/catkin_ws/src/ratio_consensus/go.csv') as csv_file:
  csv_reader = csv.reader(csv_file, delimiter=',')
  for row in csv_reader:
    for i in range(9):
      go.append(float(row[i]))

class Master:
	def __init__(self):
            self.slaves={}
            for i in range(10):
                try:
                    s=rospy.get_param("~slave"+str(i))
                    self.slaves[s]=True
                    print "slave: ", s, " added to synchronizer." 
                except:
                    pass

            for s in self.slaves.keys():
              rospy.Subscriber(s+'/ack', RTOMsg, self.sentCB)

            self.outer_iteration=Int32()
            self.outer_iteration.data=0
            self.all_info_msg=AllInfoMsg()
            self.reset_all_info()
            time.sleep(2)
            # self.pub()
            self.reset_all_info()
            self.iterate()

        def sentCB(self,msg):
            if msg.time==self.all_info_msg.time:
              self.all_info_msg.z[msg.id]=msg.z
              self.all_info_msg.P[msg.id]=msg.P
              self.all_info_msg.y[msg.id]=msg.y
              self.all_info_msg.recv[msg.id]=True
              try:
                self.slaves[msg.id]=True
              except Exception,e: print str(e)
            else:
              print("wrong time",msg.id, msg.z, msg.time, self.all_info_msg.time)

        def check_all_sent(self):
            for v in self.all_info_msg.recv:
                if v is False:
                    return False
            return True

        def reset_all_info(self):
            self.all_info_msg.time+=1
            self.all_info_msg.z=[0.0]*9
            self.all_info_msg.P=[0.0]*9
            self.all_info_msg.y=[0.0]*9
            self.all_info_msg.recv=[False]*9
            for i in range(9):
              if i==0:
                self.all_info_msg.y[i]=val[self.outer_iteration.data]-gu[i]
                print(self.all_info_msg.y)
              else:
                self.all_info_msg.y[i]=-gu[i]
              self.all_info_msg.z[i]=go[i]-gu[i]

        def iterate(self):
            print('------------------------')
            print('time',self.all_info_msg.time)
            print('z: ',self.all_info_msg.z)
            print('y: ',self.all_info_msg.y)
            print('sum: ',sum(self.all_info_msg.P))
            temp_msg=deepcopy(self.all_info_msg)
            self.reset_all_info()
            self.pub(temp_msg)
            for k,v in self.slaves.items():
                self.slaves[k]=False

        def pub(self,msg):
            all_info_pub.publish(msg)

        def outer_loop_inc(self):
          self.all_info_msg.time=0
          outer_loop_pub.publish(self.outer_iteration)
          self.reset_all_info()
          temp_msg=deepcopy(self.all_info_msg)
          self.iterate()
          self.pub(temp_msg)

        def run(self):
            now=time.time()
            while not rospy.is_shutdown():
              if time.time()-now>2:
                self.outer_iteration.data+=1
                time.sleep(.25)
                now=time.time()
                self.outer_loop_inc()
              time.sleep(.001)
              if self.check_all_sent():
                  self.iterate()

def main(args):
	manager=Master()
	try:
		manager.run()
	except KeyboardInterrupt:
		print("Draw: Shutting down")

if __name__ == '__main__':
	main(sys.argv)

