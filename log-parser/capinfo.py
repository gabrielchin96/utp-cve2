import io,string, os , shutil
import os.path,sys
from os import path
inputcapa=0
c=0
inputs=0
direction=""
pinAcap=0
pinBcap=0
pinCcap=0
pinDcap=0
for filename in os.listdir("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"):
    print('filename==',filename)
    if filename != "prob" and filename != "Averageinput_cap.txt" and filename != "width.txt" and filename != "widthA.txt" and filename != "widthB.txt" and filename != "widthC.txt" and filename != "widthD.txt":
        with io.open('C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\'+filename) as r: 
            data = r.read().splitlines()
        for inputcap in data:        
            if "direction:input" in inputcap:
                direction = "input"
            elif "direction:output" in inputcap:
                direction = "output"
            else:
                direction = direction
            if "pin(A)" in inputcap:
                pin = "A"
            elif "pin(B)" in inputcap:
                pin = "B"
            elif "pin(C)" in inputcap:
                pin = "C"
            elif "pin(D)" in inputcap:
                pin = "D"
            elif "pin(EN)" in inputcap:
                pin = "EN"
            # print("direction",direction)
            # print("inputcap",inputcap)
            if direction == "input" and "capacitance" in inputcap and "rise" not in inputcap and "fall" not in inputcap:
                cap=inputcap.replace(" ","").replace("capacitance:","").replace("pf","").replace(";","")
                if pin == "A":
                    pinAcap=cap
                elif pin == "B":
                    pinBcap=cap
                elif pin == "C":
                    pinCcap=cap
                elif pin == "D":
                    pinDcap=cap
                
                inputs+=1
                inputcapa+=float(cap)                
                print('cap',cap)
                print('inputcapa',inputcapa)
                print('inputcapa',inputs)
        avgcap=inputcapa/inputs
        if c ==0:   
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\Averageinput_cap.txt","w")
            command = [filename.replace(".txt","")+"\t"+str(pinAcap)+"\t"+str(pinBcap)+"\t"+str(pinCcap)+"\t"+str(pinDcap)+"\t"+str(avgcap)+"\n"]
            newfile.writelines(command)
            newfile.close()
            inputcapa=0
            avgcap=0
            inputs=0
            pinAcap=0
            pinBcap=0
            pinCcap=0
            pinDcap=0
            c=1
        else:
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\Averageinput_cap.txt","a")
            command = [filename.replace(".txt","")+"\t"+str(pinAcap)+"\t"+str(pinBcap)+"\t"+str(pinCcap)+"\t"+str(pinDcap)+"\t"+str(avgcap)+"\n"]
            newfile.writelines(command)
            newfile.close()
            inputcapa=0
            avgcap=0
            inputs=0
            pinAcap=0
            pinBcap=0
            pinCcap=0
            pinDcap=0
                        
