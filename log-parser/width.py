import io,string, os , shutil
import os.path,sys
from os import path

end=0
end2=0
end3=0
end4=0
end5=0
width=0
c=0
c2=0
c3=0
c4=0
c5=0
with io.open('C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\riscv_core.spc') as r: 
    data = r.read().splitlines()
    
for items in data:
    if "FILL" not in items:        
        if ("w=" in items and "Y" in items) or ("w=" in items and "Q" in items):
            for a in list(items.split(" ")):
                #print("a==",a)
                if "w=" in a:
                    width+=float(a.replace(" ","").replace("w=","").replace("u",""))
        if ".ends" in items:
            end =1 
            gate = items.replace(".ends","").replace(" ","")
        if end == 1:
            if c ==0:   
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\width.txt","w")
                command = [gate+"\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
                c=1
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\width.txt","a")
                command = [gate+"\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
            end=0
            
for items in data:
    if "FILL" not in items:        
        if "w=" in items and "A" in items:
            for a in list(items.split(" ")):
                #print("a==",a)
                if "w=" in a:
                    width+=float(a.replace(" ","").replace("w=","").replace("u",""))
        if ".ends" in items:
            end2 =1 
            gate = items.replace(".ends","").replace(" ","")
        if end2 == 1:
            if c2 ==0:   
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthA.txt","w")
                command = [gate+"A\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
                c2=1
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthA.txt","a")
                command = [gate+"A\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
            end2=0

for items in data:
    if "FILL" not in items:        
        if "w=" in items and "B" in items:
            for a in list(items.split(" ")):
                #print("a==",a)
                if "w=" in a:
                    width+=float(a.replace(" ","").replace("w=","").replace("u",""))
        if ".ends" in items:
            end3 =1 
            gate = items.replace(".ends","").replace(" ","")
        if end3 == 1:
            if c3 ==0:   
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthB.txt","w")
                command = [gate+"B\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
                c3=1
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthB.txt","a")
                command = [gate+"B\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
            end3=0
            
for items in data:
    if "FILL" not in items:        
        if "w=" in items and "C" in items:
            for a in list(items.split(" ")):
                #print("a==",a)
                if "w=" in a:
                    width+=float(a.replace(" ","").replace("w=","").replace("u",""))
        if ".ends" in items:
            end4 =1 
            gate = items.replace(".ends","").replace(" ","")
        if end4 == 1:
            if c4 ==0:   
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthC.txt","w")
                command = [gate+"C\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
                c4=1
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthC.txt","a")
                command = [gate+"C\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
            end4=0
            
for items in data:
    if "FILL" not in items:        
        if "w=" in items and "D" in items:
            for a in list(items.split(" ")):
                #print("a==",a)
                if "w=" in a:
                    width+=float(a.replace(" ","").replace("w=","").replace("u",""))
        if ".ends" in items:
            end5 =1 
            gate = items.replace(".ends","").replace(" ","")
        if end5 == 1:
            if c5 ==0:   
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthD.txt","w")
                command = [gate+"D\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
                c5=1
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\widthD.txt","a")
                command = [gate+"D\t"+str(width)+"\n"]
                newfile.writelines(command)
                newfile.close()
                width=0
            end5=0
        
            