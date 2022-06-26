import io,string, os , shutil
import os.path,sys
from os import path

arealist=[]
gates=[]
with io.open('C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\osu018_stdcells.lib') as r: 
    data = r.read().splitlines()
	
for design in data:
    if "Design :" in design:
        newdesign=design.replace(" ","").replace("*","").replace("Design:","")
        print("newdesign=",newdesign)
        if os.path.exists("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt"):
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","a")
            command = [design]
            newfile.writelines(command)
            newfile.close()
        else:            
            newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","w")
            command = [design]
            newfile.writelines(command)
            newfile.close()
    if "area :" in design:        
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","w")
        command = [design.replace(" ","").replace(";","")+"nW;\n"]
        newfile.writelines(command)
        newfile.close()
        arealist.append(design.replace(" ","").replace(";","").replace("area :",""))
        gates.append(newdesign)
    if "cell_leakage_power :" in design:        
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","w")
        command = [design.replace(" ","").replace(";","")+"nW;\n"]
        newfile.writelines(command)
        newfile.close()
    for alpha in string.ascii_uppercase:
        if "pin(" in design:
            if "pin("+alpha+")" in design:        
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","a")
                command = ["pin("+alpha+")\n"]
                newfile.writelines(command)
                newfile.close()
                break
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","a")
                command = [design.replace("{","").replace(" ","")+"\n"]
                newfile.writelines(command)
                newfile.close()
                break
    if "direction :" in design:        
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","a")
        command = [design.replace(" ","")+"\n"]
        newfile.writelines(command)
        newfile.close()
        
    if "capacitance :" in design:        
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\"+newdesign+".txt","a")
        command = [design.replace(" ","").replace(";","")+"pf;\n"]
        newfile.writelines(command)
        newfile.close()
        
        
mapped = dict(zip(gates,arealist)) 
print("mapped==",mapped)
max_key = max(mapped, key=mapped.get)
print("max_key==",max_key)
all_values = mapped.values()
max_value = max(all_values)
    