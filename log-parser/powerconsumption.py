import re
import os
import argparse
import json
import math

parser = argparse.ArgumentParser()
parser.add_argument('-lib',default='osu018_stdcells.lib')
parser.add_argument('-n', default=1)
args = parser.parse_args()

files = os.listdir()
result = list(filter(lambda v: re.match('.*postroute', v), files))

FREQ = 76.8647
VDD = 1.8

class Block:
    def __init__ (self, type, name):
        self.type = type
        self.name = name

leakage_power_unit = ""

cellList = {}
blockList = {}
outputQuantity_template = {}
inputQuantity_template = {}

def getInternalPowerFromLib(pin, type, temp):
    fall = 0
    rise = 0
    power = 0
    related_pin = ""
    for lines in temp.split("\n"):
        if ":" in lines:
            attribute = ([x.replace(" ","").replace(";","").replace("\"","") for x in lines.split(":")])
            if "internal_power" not in cellList[type][pin]:
                cellList[type][pin]['internal_power'] = {}
            if attribute[1] not in cellList[type][pin]['internal_power']:
                cellList[type][pin]['internal_power'][attribute[1]] = {"fall_power" : 0, "rise_power" : 0, "power" : 0}
            related_pin = attribute[1]
            if related_pin == 'S':
                power = 1
        elif "fall" in lines:
            fall = 1
            rise = 0
            power = 0
        elif "rise" in lines:
            rise = 1
            fall = 0
            power = 0
        elif fall == 1:
            getValue = re.findall('\".*\", ', lines)
            if getValue:
                value = getValue[0].replace('\"',"").split(",")
                cellList[type][pin]['internal_power'][related_pin]['fall_power'] = [float(x.replace(" ","")) for x in value[:-1]]
                fall = 0
        elif rise == 1:
            getValue = re.findall('\".*\", ', lines)
            if getValue:
                value = getValue[0].replace('\"',"").split(",")
                cellList[type][pin]['internal_power'][related_pin]['rise_power'] = [float(x.replace(" ","")) for x in value[:-1]]
                rise = 0
        elif power == 1:
            getValue = re.findall('\".*\", ', lines)
            if getValue:
                value = getValue[0].replace('\"',"").split(",")
                cellList[type][pin]['internal_power'][related_pin]['power'] = [float(x.replace(" ","")) for x in value[:-1]]
                power = 0
            
    


def getPinDetail(temp, type):
    internal_power = 0
    close_backet = 0
    tempInternalPower =  ""
    for lines in temp.split("\n"):
        if "pin(" in lines:
            pin = re.findall("\(.*\)", lines)[0].replace("(", "").replace(")", "")
            cellList[type][pin] = {}
            internal_power = 0
        elif "function" in lines:
            attribute = ([x.replace(";","").replace("\"","") for x in lines.split(":")])
            cellList[type][pin][attribute[0].replace(" ","")] = attribute[1][1:]
        elif ":" in lines and internal_power == 0:
            attribute = ([x.replace(" ","").replace(";","").replace("\"","") for x in lines.split(":")])
            cellList[type][pin][attribute[0]] = attribute[1]
        elif "internal_power(" in lines:
            if internal_power == 0:
                internal_power = 1
                close_backet = 1
        elif internal_power == 1:
            if "{" in lines:
                close_backet += 1
            elif "}" in lines:
                close_backet -= 1
            if close_backet == 0:
                getInternalPowerFromLib(pin, type, tempInternalPower)
                internal_power = 0
                tempInternalPower = ""
            else:
                tempInternalPower += lines + "\n"
            

def getDetail(temp):
    pin = ""
    pin_start = 0
    backet = 0
    for lines in temp.split("\n"):
        backet += len(re.findall("\{", lines))
        backet -= len(re.findall("\}", lines))
        if "cell (" in lines:
            type = re.findall("\(.*\)", lines)[0].replace("(", "").replace(")", "")
            cellList[type] = {}
            outputQuantity_template[type] = 0
            inputQuantity_template[type] = 0
        elif "pin(" in lines:
            if pin:
                getPinDetail(pin, type)
            pin = lines
            pin_start = 1
        elif backet == 0:
            pin_start = 0
            getPinDetail(pin, type)
        elif pin_start == 1:
            pin += "\n" + lines;
        elif ":" in lines and pin_start == 0:
            attribute = ([x.replace(" ","").replace(";","").replace("\"","") for x in lines.split(":")])
            cellList[type][attribute[0]] = attribute[1]
        

with open(args.lib) as fp:
    leakage_power = 0
    pin = {}
    temp = ""
    start = 0
    for lines in fp:
        if("cell (" in lines):
            start = 1
            temp = lines
        elif lines == "\n":
            if(temp):
                getDetail(temp[:-1])
        elif start == 1:
            temp += lines
        elif "leakage_power_unit" in lines:
            leakage_power_unit = lines.split(":")[1].replace("1", "").replace("\"", "").replace(";", "").replace("\n", "")

with open(result[0]) as fp:
    for lines in fp:
        if("wire" not in lines and "input" not in lines and "output" not in lines and "module" not in lines):
            if(");" in lines):
                build_block = 0
            elif build_block == 1:
                blockList[temp[1]][re.findall("\..*\(", lines)[0].replace(".","").replace("(","")] = re.findall("\(.*\)", lines)[0].replace("(","").replace(")","")
            elif any(x in lines for x in cellList):
                temp = lines.split(" ")
                build_block = 1
                blockList[temp[1]] = {'type':temp[0]}

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



totalCell = outputQuantity_template.copy()
cellDiff = outputQuantity_template.copy()
 
def getCellQuantity(outputQuantity, inputQuantity, j):
    realQuantity = {}
    
    for x in outputQuantity:
        if(inputQuantity[x] == outputQuantity[x]):
            realQuantity[x] = outputQuantity[x]
        else:
            realQuantity[x] = inputQuantity[x]

    temp = "-------------------------------------------------\nTotal Cell Used in Path "+str(j)+" and Leakage Power: \n"
    cell_count = 0
    leakage_power_count = 0
    for x in realQuantity:
        if realQuantity[x] > 0:
            temp += ("\n" + x +  "\t: " + str(realQuantity[x]) + "\tLeakage Power\t: " + "%.4f" % (realQuantity[x]*float(cellList[x]['cell_leakage_power'])) + leakage_power_unit)
            cell_count += realQuantity[x]
            leakage_power_count += realQuantity[x]*float(cellList[x]['cell_leakage_power'])
    temp += ("\n\nTotal\t: " + str(cell_count) +"\tTotal Power\t: " + "%.4f" % leakage_power_count + leakage_power_unit)
    temp += "\n-------------------------------------------------"
    
    f = open("statistic/statistic_"+str(j)+".txt", "w")
    f.write(temp)
    f.close()
    for i in realQuantity:
        totalCell[i] += realQuantity[i]
    return cell_count, leakage_power_count




def convert(value, symbol, needTimes, temp):
    if(value == 1):
        temp += symbol
    else:
        temp += "N" + symbol
    if(needTimes):
        temp += "*"
    return temp
   
def transfer(list,Y,temp):
    list_template = ['A','B','C','D']
    if(Y == 1):
        if(temp):
            temp += "+"
        for i in range(len(list)):
            if i == len(list)-1:
                temp = convert(list[i], list_template[i], 0,temp)
            else:
                temp = convert(list[i], list_template[i], 1,temp)
    return temp


def calculateProbabilityBasedOnTrueTable(expression):
    temp = ""
    for A in range(2):
        if(sum(c.isalpha() for c in expression.replace("A",""))):
            for B in range(2):
                if(sum(c.isalpha() for c in expression.replace("A","").replace("B",""))):
                    for C in range(2):
                        if(sum(c.isalpha() for c in expression.replace("A","").replace("B","").replace("C",""))):
                            for D in range(2):
                                Y = int(eval(expression.replace("!", "not").replace(" ", " and ").replace("+"," or ")))
                                temp = transfer([A,B,C,D],Y,temp)
                        else:
                            Y = int(eval(expression.replace("!", "not").replace(" ", " and ").replace("+"," or ")))
                            temp = transfer([A,B,C],Y,temp)
                else:
                    Y = int(eval(expression.replace("!", "not").replace(" ", " and ").replace("+"," or ")))
                    temp = transfer([A,B],Y,temp)
        else:
            Y = int(eval(expression.replace("!", "not").replace(" ", " and ").replace("+"," or ")))
            temp = transfer([A],Y,temp)
    return temp  

def calculateActivityFactor(lastProb):
    if lastProb == 1:
        return ("%0.6f" % (1)).ljust(22)
    return ("%0.6f" % (lastProb*(1-lastProb))).ljust(22)

def getSwitchProb(lastProb):
    return ("%0.6f" % (lastProb)).ljust(20)

def getCell(inputCell):
    return inputCell.ljust(18)
    
probability_activity_power = ""
lastProb = 1
def getUniformSwitchingProb(inputCell, pin):
    global lastProb, lastInput,probability_activity_power
    pinList = ['A','B','C','D'] 
    if "CLK" in inputCell:
        probability_activity_power += getCell(inputCell) + getSwitchProb(1) + calculateActivityFactor(1) + " "
    elif "BUF" in inputCell:
        probability_activity_power += getCell(inputCell) + getSwitchProb(lastProb) + calculateActivityFactor(lastProb) + " "
    elif "INV" in inputCell:
        probability_activity_power += getCell(inputCell) + getSwitchProb(1 - lastProb) + calculateActivityFactor(1 - lastProb) + " "
    else:
        if "DFF" not in inputCell:
            temp = calculateProbabilityBasedOnTrueTable(cellList[inputCell]['Y']['function'])
            temp = temp.replace("NA","(1-A)").replace("NB","(1-B)").replace("NC","(1-C)").replace("ND","(1-D)")
            temp = temp.replace(pin,str(lastProb)).replace("A","0.5").replace("B","0.5").replace("C","0.5").replace("D","0.5")
            lastProb = eval(temp)
        probability_activity_power += getCell(inputCell) + getSwitchProb(lastProb) + calculateActivityFactor(lastProb) + " "
    return calculateActivityFactor(lastProb)

def getEnergyTemplateIndex(load_cap):
    list = [0.01, 0.025, 0.05, 0.15, 0.3]
    for i in range(len(list)):
        if list[i] > load_cap and load_cap >= list[i-1]:
            return i
    return 4

def getInternalPower(type, temp, frequency, oldactive, newactive, load_cap, lastInput = ""):
    total = 0
    net_cap_index = getEnergyTemplateIndex(load_cap)
    outputToggleRate = newactive * frequency
    if(lastInput != ""):
        for i in temp:
            if i == lastInput:
                total += ((temp[i]['rise_power'][net_cap_index] + temp[i]['fall_power'][net_cap_index])/2)*oldactive
                newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\internalpower.txt","a")
                command = [str(type)+"\t"+str(temp[i]['rise_power'][net_cap_index])+"\t"+str(temp[i]['fall_power'][net_cap_index])+"\t"+str(net_cap_index)+"\n"]
                newfile.writelines(command)
                newfile.close()
            else:
                if "DFF" not in type:
                    total += ((temp[i]['rise_power'][net_cap_index] + temp[i]['fall_power'][net_cap_index])/2)*0.5
                    newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\internalpower.txt","a")
                    command = [str(type)+"\t"+str(temp[i]['rise_power'][net_cap_index])+"\t"+str(temp[i]['fall_power'][net_cap_index])+"\t"+str(net_cap_index)+"\n"]
                    newfile.writelines(command)
                    newfile.close()
        total = total * outputToggleRate
    elif "DFF" in type:
        total = (temp['S']['power'][net_cap_index] + temp['R']['fall_power'][net_cap_index])*frequency*oldactive
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\internalpower.txt","a")
        command = [str(type)+"\t"+str(temp['S']['power'][net_cap_index])+"\t"+str(temp['R']['fall_power'][net_cap_index])+"\t"+str(net_cap_index)+"\n"]
        newfile.writelines(command)
        newfile.close()
    else:
        total = ((temp['A']['rise_power'][net_cap_index] + temp['A']['fall_power'][net_cap_index])/2)*frequency*1
        newfile=open("C:\\Fen\\UTP\\VLSI_System\\biriscv-master_osu018\\src\\core\\synthesis\\internalpower.txt","a")
        command = [str(type)+"\t"+str(temp['A']['rise_power'][net_cap_index])+"\t"+str(temp['A']['fall_power'][net_cap_index])+"\t"+str(net_cap_index)+"\n"]
        newfile.writelines(command)
        newfile.close()
    return total

def getCapacitance(inputCell, pin):
    cap = float(cellList[inputCell][pin]['max_capacitance'])
    return cap

total_power = 0
activityFactor = 1
def getPower(type, outputPin, name, frequency, VDD, interconnect, lastInput = ""):
    global probability_activity_power, total_power, activityFactor
    parasitic_capacitance = getCapacitance(type, outputPin)
    load_capacitance,branch = getOutputCap(type, name, interconnect)
    print("type="+type+"\t"+"load_capacitance="+str(load_capacitance)+"\t"+"branch="+str(branch)+"\n")
    #wire_capacitance = 0 <ignore for now, cuz failed to PnR, missing some interconnection>
    oldactive = activityFactor
    activityFactor = float(getUniformSwitchingProb(type, lastInput))
    short_circuit_power = getInternalPower(type, cellList[type][outputPin]['internal_power'], frequency, oldactive, activityFactor, load_capacitance, lastInput)
    if lastInput == "D" and "DFF" in type:
        short_circuit_power = getInternalPower(type, cellList[type][outputPin]['internal_power'], frequency, oldactive, activityFactor, load_capacitance)
    static = float(cellList[type]['cell_leakage_power'])
    switch_power = (parasitic_capacitance + load_capacitance)*activityFactor*frequency*(VDD**2)
    probability_activity_power += ("%0.6f" % (parasitic_capacitance)).ljust(20) 
    if load_capacitance != 0:
        probability_activity_power += ("%0.6f" % (load_capacitance)).ljust(15) 
    else:
        probability_activity_power += "".ljust(15) 
    probability_activity_power += ("%0.4f" % (frequency)).ljust(15) 
    probability_activity_power += str(VDD).ljust(13)
    probability_activity_power += ("%0.6f" % (static)).ljust(17)
    probability_activity_power += ("%0.6f" % (switch_power)).ljust(20)
    probability_activity_power += ("%0.6f" % (short_circuit_power)).ljust(20)
    probability_activity_power += ("%0.6f" % (switch_power + static/1000)).ljust(7)
    total_power += (switch_power + static/1000 + short_circuit_power)
    probability_activity_power += "\n"
    
def getBlockDiagName(name):
    if name[2] in name[0]:
        return name[0]
    else:
        return name[2] + name[0].replace(name[2] + "_", "")


def getOutputPinConnectToWhere(i, interconnect, list):
    for pinName in list:
        if pinName in i:
            if i[pinName].replace("\\", "").replace(" ", "") == interconnect.replace("\\", "").replace(" ", ""):
                return pinName
    return False

def getOutputCap(type, name, interconnect):
    global blockList
    cap = 0
    branch = 0
    for i in blockList:
        if "CLK" in type:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['CLK'])
        else:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['A','B','C','D'])
        if temp:
            cap += float(cellList[blockList[i]['type']][temp]['capacitance'])
            branch+=1
            #print('capacitance========',str(float(cellList[blockList[i]['type']][temp]['capacitance'])))
    return cap,branch

def getDiagram(j, outputQuantity_template, inputQuantity_template):
    global probability_activity_power, total_power, lastInput
    lastInput = ""
    outputQuantity = outputQuantity_template.copy()
    inputQuantity = inputQuantity_template.copy()
    blockdiag = "blockdiag {span_width=300;"
    with open('critical/critical_'+str(j)+'.txt') as fp:
    #with open('critical/critical_11.txt') as fp:
        fold = 0
        for lines in fp:
            interconnect = re.findall("ps .*:", lines)[0].replace("ps ", "").replace(" ", "").replace(":", "").replace("\\", "")
            output = re.findall("\:.*\-", lines)[0].replace(" ","").replace(":","").replace("-","").split("/")
            input = re.findall(">.*", lines)[0].replace(">","").replace(" ","").split("/")
            outputType = blockList[output[0]]['type']
            output.append(outputType)
            outputQuantity[outputType] += 1
            inputType = blockList[input[0]]['type']
            input.append(inputType)
            inputQuantity[inputType] += 1
            print("outputoutput",input)
            getPower(outputType, output[1], output[0], FREQ, VDD, interconnect, lastInput)
            lastInput = input[1]
            blockdiag += getBlockDiagName(output) + " -> " + getBlockDiagName(input) + '[label="' + interconnect + '"];'
            fold = fold + 1
            if(fold == 6):
                blockdiag += getBlockDiagName(output) + " -> " + getBlockDiagName(input) + '[folded];'
                fold = 0
    getPower(inputType, 'Q', input[0], FREQ, VDD, blockList[input[0]]['Q'], 'D')
    blockdiag += "}";
    f = open("diagram/critical_path_"+str(j)+".diag", "w")
    f.write(blockdiag)
    f.close()
    os.system("blockdiag diagram/critical_path_"+str(j)+".diag")
    os.remove("diagram/critical_path_"+str(j)+".diag")
    
    f = open("PowerConsumption.txt", "w")
    f.write("CELL".ljust(15) + "Switching Prob".ljust(20) + "Activity Factor".ljust(25) + \
    "Parasitic Cap/pF".ljust(21) + "Load Cap/pF".ljust(14) + "Freq/MHz".ljust(16) + "VDD/V".ljust(11)  + "StaticPWR/nW".ljust(18) +\
    "SwitchPWR/uW".ljust(17) + "ShortCircuitPWR/nW".ljust(24) + "Total/uW".ljust(15) + "\n\n")
    f.write(probability_activity_power)
    f.write("\nTotal Power: " + "%0.4f" % (total_power/1000) + " mW")
    f.close()
    return getCellQuantity(outputQuantity,inputQuantity, j)


cellStaticLeakage = []
for j in range(1,args.n+1):
    temp = ""
    i = 1
    with open('critical/critical_'+str(j)+'.txt') as fp:
    #with open('critical/critical_11.txt') as fp:
        temp += "-------------------------------------------------"
        for lines in fp:
            interconnect = re.findall("ps .*:", lines)[0].replace("ps ", "").replace(" ", "").replace(":", "").replace("\\", "")
            output = re.findall("\:.*\-", lines)[0].replace(" ","").replace(":","").replace("-","").split("/")
            input = re.findall(">.*", lines)[0].replace(">","").replace(" ","").split("/")
            output.append(blockList[output[0]]['type'])
            input.append(blockList[input[0]]['type'])
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
    cellStaticLeakage.append(getDiagram(j, outputQuantity_template, inputQuantity_template))
    print(("Path " + str(j)).ljust(9) + " process done !")

num = {"AND2X2":1414, "AOI21X1":8848, "AOI22X1":1616, "BUFX2":119, "DFFPOSX1":992, "DFFSR":5556, "INVX1":9860, "MUX2X1":1744, "NAND2X1":9231, "NAND3X1":6334, "NOR2X1":10700, "NOR3X1":1315, "OAI21X1":21421, "OAI22X1":2481, "OR2X2":597, "XNOR2X1":1706, "XOR2X1":702}
total = 0    
for i in num:
    total += float(cellList[i]['cell_leakage_power'])*num[i]
    print((i).ljust(9)+"\t--> Leakage\t:" + "%0.6f" % float(cellList[i]['cell_leakage_power']) + "\t Total:\t" + "%0.6f" % (float(cellList[i]['cell_leakage_power'])*num[i]))
print("Total Leakage Power\t:\t" + "%0.6f" % total)