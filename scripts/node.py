#!/usr/bin/env python

import time
import rospy
from ratio_consensus.msg import yzMsg
import csv

with open('employee_birthday.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
            line_count += 1
    print(f'Processed {line_count} lines.')

rospy.init_node('ratio_consensus', anonymous=True)

if rospy.has_param("~gu"):
    gu = rospy.get_param("~gu")

if rospy.has_param("~go"):
    go = rospy.get_param("~go")

if rospy.has_param("~id"):
    ident = int(rospy.get_param("~id"))

if rospy.has_param("~master"):
    master = rospy.get_param("~master")

neighbor_list=[]

if ident==1:
    neighbor_list.append(2)
    neighbor_list.append(9)
elif ident==9:
    neighbor_list.append(8)
    neighbor_list.append(1)
elif:
    neighbor_list.append(ident+1)
    neighbor_list.append(ident-1)

pub = rospy.Publisher('/yz',yz_msg,queue_size=100)
neighbor_list


class Node:
	def __init__(self):
            self.yz_msg=yzMsg()
            self.yz_msg.iteration=0
            if master:
                self.y
            else:
                self.yz_msg.y=-g_u
                self.yz_msg.z=g_o-g_u
            self.iteration
            self.z={}
            for n in neighbor_list:
                self.z[n]={}

        def check_req():
            for yz in self.yz.values():
                if yz.get(self.iteration)==None:
                    return False
            return True


        def yzCB(self,msg):
            self.yz=

            self.yz[msg.iteration]=yzMsg()
            self.yz[msg.iteration].y=msg.y
            self.yz[msg.iteration].z=msg.z
            if self.check_req():
                self.publish_yz()

        def publish_yz(self):
            #calculate yz
            #Hardcoded
            z_sum=0
            y_sum=0
            for yz in self.yz.values():
                z_sum+=yz.z
                y_sum+=yz.y

            y=1./3.*(self.z_msg.y+y_sum)
            z=1./3.*(self.z_msg.z+z_sum)
            self.yz_msg.y=y
            self.yz_msg.z=z
            self.yz_msg.iteration+=1
            pub.publish(self.yz_msg)

def main(args):
	node=Node()
        for n in neighbor_list:
            rospy.Subscriber(str(n)+'/yz', yzMsg, node.yzCB)
	try:
		node.run()
	except KeyboardInterrupt:
		print("Draw: Shutting down")

if __name__ == '__main__':
	main(sys.argv)
