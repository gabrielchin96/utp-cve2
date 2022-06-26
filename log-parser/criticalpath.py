import re
import os
import argparse
import json
import math

parser = argparse.ArgumentParser()
parser.add_argument('-lib',default='osu018_stdcells.lib')
parser.add_argument('-n', default=20)
args = parser.parse_args()

files = os.listdir()
result = list(filter(lambda v: re.match('.*postroute', v), files))

class Block:
    def __init__ (self, type, name):
        self.type = type
        self.name = name

cellList = []
outputQuantity_template = {}
inputQuantity_template = {}
blockList = []

with open(args.lib) as fp:
    for lines in fp:
        if("Design" in lines):
            type = re.findall(":.*\*", lines)[0].replace(":", "").replace(" ", "").replace("*", "")
            cellList.append(type)
            outputQuantity_template[type] = 0
            inputQuantity_template[type] = 0

with open(result[0]) as fp:
    for lines in fp:
        if("wire" not in lines and "input" not in lines and "output" not in lines and "module" not in lines):
            if(");" in lines):
                build_block = 0
            elif any(x in lines for x in cellList):
                temp = lines.split(" ")
                blockList.append(Block(temp[0], temp[1]))







critical = ""
start = 0
i = 1
with open('reports/reg_to_reg_max.log') as fp:
    for lines in fp:
        if i == args.n+1:
            break
        elif 'Path' in lines:
            start = 1
        elif 'skew' in lines:
            f = open("critical/critical_"+str(i)+".txt", "w")
            f.write(critical)
            f.close()
            critical = ""
            start = 0
            i += 1
        elif start == 1:
            if(lines != "\n"):
                critical += lines
            







result = list(filter(lambda v: re.match('.*spc', v), files))

subckt = {}

with open(result[0]) as fp:
    start = 0
    name = ""
    pfet = 0
    nfet = 0
    for lines in fp:
        if ".subckt" in lines:
            start = 1
            name = lines.split(" ")[1]
        elif ".ends" in lines: 
            start = 0
            subckt[name] = {"pfet":pfet, "nfet":nfet}
            pfet = 0
            nfet = 0
        elif start == 1:
            if "pfet" in lines:
                pfet += 1
            elif "nfet" in lines:
                nfet += 1

subckt.popitem()

f = open("statistic/total_statistic.txt", "w")
for x in subckt:
    f.write(x + "\t: PMOS:\t" + str(subckt[x]['pfet']) + "\tNMOS:\t" + str(subckt[x]['nfet']) + "\n")
f.close()
 
 
 
 
 
totalCell = outputQuantity_template.copy()
cellDiff = outputQuantity_template.copy()
 
def getFetQuantity(outputQuantity, inputQuantity, subckt, j):
    realQuantity = {}
    
    for x in outputQuantity:
        if(inputQuantity[x] == outputQuantity[x]):
            realQuantity[x] = outputQuantity[x]
        else:
            realQuantity[x] = inputQuantity[x]

    temp = "-------------------------------------------------\nTotal Cell and Mosfet used in Path "+str(j)+": \n"
    total = 0
    pfetTotal = 0
    nfetTotal = 0
    for x in realQuantity:
        if realQuantity[x] > 0:
            temp += ("\n" + x +  "\t: " + str(realQuantity[x])\
            + "\tPMOS: \t" + str(realQuantity[x]*subckt[x]['pfet']) \
            + "\tNMOS: \t" + str(realQuantity[x]*subckt[x]['nfet']))
            total += realQuantity[x]
            pfetTotal += realQuantity[x]*subckt[x]['pfet']
            nfetTotal += realQuantity[x]*subckt[x]['nfet']
    temp += ("\n\nTotal\t: " + str(total) + "\tTotal:\t" + str(pfetTotal) + "\tTotal:\t" + str(nfetTotal) )
    temp += "\n-------------------------------------------------"
    
    f = open("statistic/statistic_"+str(j)+".txt", "w")
    f.write(temp)
    f.close()
    for i in realQuantity:
        totalCell[i] += realQuantity[i]
    return [total, pfetTotal, nfetTotal]
 
 
 
 
 
def getBlockDiagName(name):
    if name[2] in name[0]:
        return name[0]
    else:
        return name[2] + name[0].replace(name[2] + "_", "")


def getDiagram(j, outputQuantity_template, inputQuantity_template):
    outputQuantity = outputQuantity_template.copy()
    inputQuantity = inputQuantity_template.copy()
    statistic = ""
    blockdiag = "blockdiag {span_width=300;"
    a=0
    with open('critical/critical_'+str(j)+'.txt') as fp:
        fold = 0
        for lines in fp:
            interconnect = re.findall("ps .*:", lines)[0].replace("ps ", "").replace(" ", "").replace(":", "").replace("\\", "")
            output = re.findall("\:.*\-", lines)[0].replace(" ","").replace(":","").replace("-","").split("/")
            input = re.findall(">.*", lines)[0].replace(">","").replace(" ","").split("/")
            for x in blockList:
                if output[0] == x.name:
                    output.append(x.type)
                    outputQuantity[x.type] += 1
                if input[0] == x.name:
                    input.append(x.type)
                    inputQuantity[x.type] += 1
            blockdiag += getBlockDiagName(output) + " -> " + getBlockDiagName(input) + '[label="' + interconnect + '"];'
            if a ==0:
                a=1
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path"+str(j)+".txt","w")
                cleanblock= getBlockDiagName(input).split('_')[0]
                command = [cleanblock+"\n"]
                newfile.writelines(command)
                newfile.close()
            else:
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\gates\\gates_path"+str(j)+".txt","a")
                cleanblock= getBlockDiagName(input).split('_')[0]
                command = [cleanblock+"\n"]
                newfile.writelines(command)
                newfile.close()
            fold = fold + 1
            if(fold == 6):
                blockdiag += getBlockDiagName(output) + " -> " + getBlockDiagName(input) + '[folded];'
                fold = 0


    blockdiag += "}";
    f = open("diagram/critical_path_"+str(j)+".diag", "w")
    f.write(blockdiag)
    f.close()
    os.system("blockdiag diagram/critical_path_"+str(j)+".diag")
    os.remove("diagram/critical_path_"+str(j)+".diag")
    return getFetQuantity(outputQuantity,inputQuantity, subckt, j)





fetTotal = []
for j in range(1,args.n+1):
    temp = ""
    i = 1
    with open('critical/critical_'+str(j)+'.txt') as fp:
        temp += "-------------------------------------------------"
        for lines in fp:
            interconnect = re.findall("ps .*:", lines)[0].replace("ps ", "").replace(" ", "").replace(":", "").replace("\\", "")
            output = re.findall("\:.*\-", lines)[0].replace(" ","").replace(":","").replace("-","").split("/")
            input = re.findall(">.*", lines)[0].replace(">","").replace(" ","").split("/")
            for x in blockList:
                if output[0] == x.name:
                    output.append(x.type)
                if input[0] == x.name:
                    input.append(x.type)
            temp += "\nBlock: " + str(i)
            temp += "\nOutput pin: "
            temp += str(output)
            temp += "\nInterconnect Wire: "
            temp += str(interconnect)
            temp += "\nInput pin: "
            temp += str(input)
            temp += "\n-------------------------------------------------"
            i = i + 1

    f = open("longest/longestpath_"+str(j)+".txt", "w")
    f.write(temp)
    f.close()
    fetTotal.append(getDiagram(j, outputQuantity_template, inputQuantity_template))
    print(("Path " + str(j)).ljust(9) + " process done !")
 
 
pmos_max = fetTotal[0][1]
nmos_max = fetTotal[0][2]
for i in range(1,len(fetTotal)):
    if pmos_max < fetTotal[i][1]:
        pmos_max = fetTotal[i][1]  
    if nmos_max < fetTotal[i][2]:
        nmos_max = fetTotal[i][2]  


pmos_max_desc = "\n-------------------------------------------------"
nmos_max_desc = "\n-------------------------------------------------"    
f = open("statistic/total_statistic.txt", "a")
j = 1
for i in fetTotal:
    f.write("\nPath"+str(j)+"-->\tCell\t: " + str(i[0]) + "\tPMOS:\t" + str(i[1]) + "\tNMOS:\t" + str(i[2]))
    if i[1] == pmos_max:
        pmos_max_desc += "\nPath " + str(j) + "\thaving largest amount of PMOS :\t" + str(i[1])
    if i[2] == nmos_max:
        nmos_max_desc += "\nPath " + str(j) + "\thaving largest amount of NMOS :\t" + str(i[2])
    j += 1
total = [sum(x) for x in zip(*fetTotal)]
nominal = [float(x/len(fetTotal)) for x in total]
standard_deviation = [math.sqrt(sum([(x[y]-nominal[y])**2 for x in fetTotal])/(len(fetTotal)-1)) for y in range(len(fetTotal[0]))]
f.write("\n\t\tTotal\t: " + str(total[0]) + "\tTotal:\t" + str(total[1]) + "\tTotal:\t" + str(total[2]))
f.write("\n\t\tMEAN\t: " + "%.2f" % nominal[0] + "\tMEAN:\t" + "%.2f" % nominal[1] + "\tMEAN:\t" + "%.2f" % nominal[2])
f.write("\n\t\tSTD\t: " + "%.2f" % standard_deviation[0] + "\tSTD:\t" + "%.2f" % standard_deviation[1] + "\tSTD:\t" + "%.2f" % standard_deviation[2])
f.write(pmos_max_desc)
f.write(nmos_max_desc)
f.write("\n-------------------------------------------------")
for i in totalCell:
    if(totalCell[i]):
        f.write(("\n" + i + ":").ljust(20) + str(totalCell[i]))
f.close()