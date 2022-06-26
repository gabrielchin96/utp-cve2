import ttg,io
print(ttg.Truths(['A', 'B', 'C'], ['not ((A or B) and C)']))
newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\prob\\OAI21X1.txt","w")
command = [str(ttg.Truths(['A', 'B', 'C'], ['not ((A or B)and C)']))+"\n"]
newfile.writelines(command)
newfile.close()

print(ttg.Truths(['A', 'B', 'C'], ['not ((A or B) and (C or D))']))
newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\prob\\OAI22X1.txt","w")
command = [str(ttg.Truths(['A', 'B', 'C'], ['not ((A or B)and C)']))+"\n"]
newfile.writelines(command)
newfile.close()

completelist=[]
usedlist=[]
swithcing=[]
list3=[]
with io.open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\prob\\OAI22X1.txt") as r: 
    truth = r.read().splitlines()

for t in truth:
    if "0" in t or "1" in t:
        newt=t.replace(" ","").replace("|","")
        #print("newt==",newt)
        listit=list(newt)
        #print('listit==',listit)
        #print(len(listit))
        if listit[-1] == "1":
            print("listit==",listit)
            completelist.append(listit[:-1])
print("completelist==",completelist)
for items in completelist:
    for a in items:
        if a == "0":
            if "Pa" not in usedlist:
                Pa="(1-Pa)*"
                usedlist.append("Pa")
                swithcing.append(Pa)
            elif "Pb" not in usedlist:
                Pa="(1-Pb)*"
                usedlist.append("Pb")
                swithcing.append(Pa)
            elif "Pc" not in usedlist:
                Pa="(1-Pc)"
                usedlist.append("Pc")
                swithcing.append(Pa)
            elif "Pd" not in usedlist:
                Pa="(1-Pd)"
                usedlist.append("Pd")
                swithcing.append(Pa)
        else:
            if "Pa" not in usedlist:
                Pa="Pa*"
                usedlist.append("Pa")
                swithcing.append(Pa)
            elif "Pb" not in usedlist:
                Pa="Pb*"
                usedlist.append("Pb")
                swithcing.append(Pa)
            elif "Pc" not in usedlist:
                Pa="Pc"
                usedlist.append("Pc")
                swithcing.append(Pa)
            elif "Pd" not in usedlist:
                Pa="Pd"
                usedlist.append("Pd")
                swithcing.append(Pa)
                
    usedlist.clear()
lst2 = []
for i in range(0, len(swithcing), 3):
    lst2.append(swithcing[i] + swithcing[i+1]+swithcing[i+2])
for s in lst2:
    # print('lst2[:-1]=',lst2[-1])
    # print("s=",s)
    if s == lst2[-1]:
        list3.append("("+s+")")
    else:
        list3.append("("+s+")+")
ok="".join(list3)
print(ok)
newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates_info\\prob\\OAI22X1.txt","a")
command = ["Switching Probability: "+ok]
newfile.writelines(command)
newfile.close()

        

