#!/usr/bin/env python
import sys
import time
import rospy
# from ratio_consensus.msg import yzMsg
from geometry_msgs.msg import Quaternion
from std_msgs.msg import Int32 as IntMsg

import csv


rospy.init_node('ratio_consensus', anonymous=True)

val=[]
line_iter=0

if rospy.has_param("~id"):
    ident = int(rospy.get_param("~id"))

if rospy.has_param("~master"):
    master = rospy.get_param("~master")

if master==True:
    with open('/home/aaron/catkin_ws/src/ratio_consensus/scripts/scaled_interp_Pref.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            val.append(float(row[0]))
            line_count+=1
        max_iter=line_count


with open('/home/aaron/catkin_ws/src/ratio_consensus/scripts/gu.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        gu=(float(row[ident-1]))

with open('/home/aaron/catkin_ws/src/ratio_consensus/scripts/go.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        go=(float(row[ident-1]))

neighbor_list=[]

if ident==1:
    neighbor_list.append(2)
    neighbor_list.append(9)
elif ident==9:
    neighbor_list.append(8)
    neighbor_list.append(1)
else:
    neighbor_list.append(ident+1)
    neighbor_list.append(ident-1)

pub = rospy.Publisher('yz',Quaternion,queue_size=1)
reqpub=[]
for n in neighbor_list:
    reqpub.append(rospy.Publisher('/'+str(n)+'/req',IntMsg,queue_size=1))
neighbor_list


class Node:
	def __init__(self):
            self.yz_msg={}
            # self.yz_msg=yzMsg()
            self.yz_msg[0]=Quaternion()
            self.yz_msg[0].x=0
            self.yz_msg[0].w=ident
            if master:
                self.yz_msg[0].y=val[0]-gu
            else:
                self.yz_msg[0].y=-gu
            self.yz_msg[0].z=go-gu
            self.iteration=0
            self.iteration2=0
            self.yz={}
            for n in neighbor_list:
                self.yz[n]={}
            time.sleep(ident/10.)
            self.pub(0)

        def check_req(self):
            for yz in self.yz.values():
                if yz.get(self.iteration)==None:
                    return False
            return True

        def req(self):
            for n in reqpub:
                n.publish(self.iteration)

        def reqCB(self,msg):
            self.pub(msg.data)

        def yzCB(self,msg):
            # self.yz[int(msg.w)]={}
            if self.yz.get(int(msg.w)) == None:
                return
            self.yz[int(msg.w)][int(msg.x)]={}
            self.yz[int(msg.w)][int(msg.x)]=Quaternion()
            self.yz[int(msg.w)][int(msg.x)].y=msg.y
            self.yz[int(msg.w)][int(msg.x)].z=msg.z
            self.yz[int(msg.w)][int(msg.x)].w=msg.w
            self.yz[int(msg.w)][int(msg.x)].x=msg.x
            if self.check_req():
                self.update_yz(self.iteration)

        def update_yz(self,iteration):
            z_sum=0
            y_sum=0

            if iteration>0:
                for yz in self.yz.values():
                    try:
                        z_sum+=yz[iteration].z
                        y_sum+=yz[iteration].y
                    except:
                        return

            try:
                y=1./3.*(self.yz_msg[iteration].y+y_sum)
                z=1./3.*(self.yz_msg[iteration].z+z_sum)
            except:
                return
            self.yz_msg[iteration+1]=Quaternion()
            self.yz_msg[iteration+1].y=y
            self.yz_msg[iteration+1].z=z
            self.yz_msg[iteration+1].x=iteration+1
            self.yz_msg[iteration+1].w=ident
            self.pub(iteration+1)
            self.iteration+=1

        def pub(self,data):
            if self.yz_msg.get(data) is None:
                return
            pub.publish(self.yz_msg[data])

        def update_y(self):
            try:
                self.yz_msg[self.iteration].y+=(val[self.iteration]-val[self.iteration-1])
            except:
                self.iteration-=1

        def run(self):
            while not rospy.is_shutdown():
                if master:
                    self.iteration2+=1
                    self.update_y()

                # f = open(str(ident)+".csv", "w")
                # f.write(str(gu+(self.yz_msg.y/self.yz_msg.z)*(go-gu)))
                self.req()
                # self.pub()
                time.sleep(.001)


def main(args):
	node=Node()
        rospy.Subscriber('req', IntMsg, node.reqCB)
        time.sleep(1)
        for n in neighbor_list:
            rospy.Subscriber('/'+str(n)+'/yz', Quaternion, node.yzCB)
	try:
		node.run()
	except KeyboardInterrupt:
		print("Draw: Shutting down")

if __name__ == '__main__':
	main(sys.argv)
