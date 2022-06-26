import io,string, os , shutil
import os.path,sys
from os import path
count = 0
changes=0
halt=0
inputnumber=0
subin =0.5
usedlist=[]
with io.open('C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path1.txt') as r: 
    data = r.read().splitlines()

newlist=[]
for d in data:
    if "_" in d:
        changes=1
        clean=d.split('_')[0]
        #print("clean==",clean)
        newlist.append(clean)

if changes ==1:
    for items in newlist:
        if count == 0:
            count=1
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path1.txt","w")
            command = [items+"\n"]
            newfile.writelines(command)
            newfile.close()
        else:
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path1.txt","a")
            command = [items+"\n"]
            newfile.writelines(command)
            newfile.close()
 
with io.open('C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path1.txt') as r: 
    newdata = r.read().splitlines()
    
for data in newdata:
    halt=0
    if os.path.exists("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+data+".txt"):
        with io.open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+data+".txt") as r: 
            checkdata = r.read().splitlines()
        for stuff in checkdata:
            if "input_ports:" in stuff:
                halt=1
                print(stuff)
        if data not in usedlist and halt==0:
            with io.open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+data+".txt") as ra: 
                da = ra.read().splitlines()
            for items in da:
                if "input" in items:
                    inputnumber+=1
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+data+".txt","a")
            command = ["input_ports:"+str(inputnumber)+"\n"]
            print(command)
            newfile.writelines(command)
            newfile.close()
            usedlist.append(data)
            inputnumber=0
        


        