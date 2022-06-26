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
            pin += "\n" + lines
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
        if i == int(args.n)+1:
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
            subckt[name] = {"pmos":pfet, "nmos":nfet}
            pfet = 0
            nfet = 0
        elif start == 1:
            if "pfet" in lines:
                if 'Y' in lines:
                    pfet += int(re.findall("w=.*u ", lines)[0].replace("w=","").replace("u ",""))
            elif "nfet" in lines:
                if 'Y' in lines:
                    nfet += int(re.findall("w=.*u ", lines)[0].replace("w=","").replace("u ",""))

#print(subckt)

def getEnergyTemplateIndex(load_cap):
    list = [0.01, 0.025, 0.05, 0.15, 0.3]
    for i in range(len(list)):
        if list[i] > load_cap and load_cap >= list[i-1]:
            return i
    return 4

def getParasiticCap(inputCell, pin):
    return float(cellList[inputCell][pin]['max_capacitance'])

def getOutputPinConnectToWhere(i, interconnect, list):
    for pinName in list:
        if pinName in i:
            if i[pinName].replace("\\", "").replace(" ", "") == interconnect.replace("\\", "").replace(" ", ""):
                return pinName
    return False

def getLoadCap(type, name, interconnect):
    global blockList
    cap = 0
    for i in blockList:
        if "CLK" in type:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['CLK'])
        else:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['A','B','C','D'])
        if temp:
            cap += float(cellList[blockList[i]['type']][temp]['capacitance'])
    return cap

def getLoadNumber(type, interconnect):
    global blockList
    number = 0
    for i in blockList:
        if "CLK" in type:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['CLK'])
        else:
            temp = getOutputPinConnectToWhere(blockList[i], interconnect, ['A','B','C','D'])
        if temp:
            number += 1
    return number

def getOutputCap(cell):
    return getLoadCap(path[cell]['type'], cell, path[cell]['outputWire']) #+ getParasiticCap(path[cell]['type'], path[cell]['outputPin']) #+ wireCapList[cell]

def getLogicalEffort(cell):
    return float(cellList[blockList[cell]['type']][path[cell]['inputPin']]['capacitance']) / 0.00932456

def getPathLogicalEffort(path):
    effort = 1
    for cell in path:
        effort = effort * getLogicalEffort(cell)
    return effort

def getPathBranchingEffort(path, outCapList):
    for i in range(len(path)):
        cell = list(path)[i]
        if "DFF" not in path[cell]['type']:
            previousLoadCap = outCapList[list(path)[i-1]]
            inputCap = float(cellList[blockList[cell]['type']][path[cell]['inputPin']]['capacitance']) 
            return (previousLoadCap / inputCap)

def getPathBranchingEffort2(cell, path, outCapList, nextStageCin):
    start = 0
    nextLoadCap = 0
    for curr in path:
        if curr == cell:
            start = 1
        elif start == 1:
            nextLoadCap = outCapList[cell] - float(cellList[blockList[curr]['type']][path[curr]['inputPin']]['capacitance']) + nextStageCin #- wireCapList[cell]
            break
    if nextLoadCap == 0 and start == 1:
        nextLoadCap = outCapList[cell] - float(cellList['DFFSR']['D']['capacitance']) + nextStageCin #- wireCapList[cell]
    return (nextLoadCap / nextStageCin)

def getPathElectricalEffort(outCapList):
    firstCell = list(outCapList)[-1]
    return outCapList[list(outCapList)[-1]] \
        / float(cellList[blockList[firstCell]['type']][path[firstCell]['inputPin']]['capacitance'])  #outCapList[list(outCapList)[0]]

def getPathEffort(path, outCapList):
    return getPathLogicalEffort(path) * getPathElectricalEffort(outCapList) * getPathBranchingEffort(path, outCapList)

def getStageEffort(pathEffort, bestNumberofStage):
    return pathEffort ** (1 / bestNumberofStage)

def getBestNumberofStage(pathEffort):
    return math.log(pathEffort, 4)

def deriveCin(cell, Cout, logicalEffort, StageEffort):
    # F=GBH, Cin = Cout * gi * bi / fi(min)
    return Cout * logicalEffort * getPathBranchingEffort2(cell, path, outCapList, Cout) / StageEffort

capTransList = {}

def capacitanceTransformation(path, StageEffort):
    Cin = outCapList[list(path)[-1]]
    for cell in reversed(path):
        #Cin =  deriveCin(Cin, getLogicalEffort(cell), StageEffort)
        Cin =  deriveCin(cell, Cin , getLogicalEffort(cell), StageEffort)
        capTransList[cell] = Cin
    #print(capTransList)

def printStatistic(cell, inputPin, inputCap, outputCap, parasitic, logical, branching, electrical, showScaling = 0):
    print((cell).ljust(20) \
        + (path[cell]['type']).ljust(10) + " " \
        + (inputPin).ljust(9) \
        + (" %.5f" %inputCap).ljust(9) \
        + (" %.5f" %outputCap).ljust(12) \
        + (" %.5f" %parasitic).ljust(10) \
        + (" %.5f" %logical).ljust(14) \
        + (" %.5f" %branching).ljust(18) \
        + (" %.5f" %electrical).ljust(20) \
        + (" %.5f" % (float(logical)*float(branching)*float(electrical))).ljust(18),end="")
    if showScaling == 0:
        print("\n")
    else:
        print((" %.5f" %scalingFactor[cell]).ljust(18))

def printTitle(showScaling):
    if showScaling == 0:
        print(("CELL NAME").ljust(20) + ("CELL TYPE").ljust(10) + " " + ("Input Pin").ljust(9) + (" InputCap").ljust(9) + (" OutputCap").ljust(12) + (" Parasitic").ljust(10) + (" LogicalEffort").ljust(14) + (" BranchingEffort").ljust(18) + (" ElectricalEffort").ljust(20) + (" StageEffort").ljust(18))
    else:
        print(("CELL NAME").ljust(20) + ("CELL TYPE").ljust(10) + " " + ("Input Pin").ljust(9) + (" InputCap").ljust(9) + (" OutputCap").ljust(12) + (" Parasitic").ljust(10) + (" LogicalEffort").ljust(14) + (" BranchingEffort").ljust(18) + (" ElectricalEffort").ljust(20) + (" StageEffort").ljust(18) + (" ScalingFactor").ljust(18))

for j in range(1,int(args.n)+1):
    path = {}
    outCapList = {}
    branchList = {}
    temp = ""
    with open('critical/critical_'+str(j)+'.txt') as fp:
        temp += "-------------------------------------------------"
        input = ['','','']
        output = ['','','']
        for lines in fp:
            output = re.findall("\:.*\-", lines)[0].replace(" ","").replace(":","").replace("-","").split("/")
            output.append(blockList[output[0]]['type'])
            interconnect = re.findall("ps .*:", lines)[0].replace("ps ", "").replace(" ", "").replace(":", "").replace("\\", "")
            if input[-1] != '' and "DFF" not in input[-1]:
                path[input[0]] = {"type": input[-1], "outputPin":output[1], "inputPin":input[1], "outputWire": interconnect}
            input = re.findall(">.*", lines)[0].replace(">","").replace(" ","").split("/")
            input.append(blockList[input[0]]['type'])
            temp += "\nBlock: " + str(len(path)+1)
            temp += "\nOutput pin: "
            temp += str(output)
            temp += "\nInterconnect Wire: "
            temp += str(interconnect)
            temp += "\nInput pin: "
            temp += str(input)
            temp += "\n-------------------------------------------------"
        #path[input[0]] = {"type": input[-1], "outputPin":"Q", "inputPin":input[1]}
    #print(path)
    for cell in path:
        branchList[cell] = getLoadNumber(path[cell]['type'], path[cell]['outputWire'])
        outCapList[cell] = getOutputCap(cell)
    #print(outCapList)
    pathEffort = getPathEffort(path, outCapList)
    #print(branchList)
    #print("Path Effort: " + str(pathEffort))

    # ******* IF POSSIBLE TO CHANGE LOGIC: BEST NUMBER ***********
    #bestNumberofStage = getBestNumberofStage(pathEffort)
    #print(bestNumberofStage)
    #bestStageEffort = getbestStageEffort(pathEffort, bestNumberofStage)
    # ******* IF POSSIBLE TO CHANGE LOGIC: BEST NUMBER ***********
    
    #print("Stage: " + str(len(path)))
    StageEffort = getStageEffort(pathEffort, len(path))
    #print("Stage Effort: " + str(StageEffort))
    capacitanceTransformation(path, StageEffort)
    scalingFactor = {}
    for i in range(len(path)):
        cell = list(path)[i]
        if i == len(path)-1:
            cout = outCapList[cell]
        else:
            nextCell = list(path)[i+1]
            cout = outCapList[cell] - float(cellList[blockList[nextCell]['type']][path[nextCell]['inputPin']]['capacitance']) + capTransList[nextCell]
        # d = g(Cout/Cin) + p
        cin = capTransList[cell]
        scalingFactor[cell] = capTransList[cell] / getLogicalEffort(cell) / StageEffort
        parasitic_delay = float(int(subckt[path[cell]['type']]['pmos']) + int(subckt[path[cell]['type']]['nmos'])) / 3
        # d = gh + p, Pinv = 88.1477 ps, (9.32 * (1.7+1.47) / 2) , [(0.0309+0.00921)/2]n --> p
        #print(getLogicalEffort(cell)*getPathBranchingEffort2(cell, path, outCapList, cout)* cout/cin)
    #print(scalingFactor)

    print("Before Optimize:")
    printTitle(0)
    delay = 0
    for cell in path: 
        cin = float(cellList[blockList[cell]['type']][path[cell]['inputPin']]['capacitance'])
        cout = outCapList[cell]
        para = float(int(subckt[path[cell]['type']]['pmos']) + int(subckt[path[cell]['type']]['nmos'])) / 3
        logic = getLogicalEffort(cell)
        be = getPathBranchingEffort2(cell, path, outCapList, float(cellList[blockList[cell]['type']][path[cell]['inputPin']]['capacitance']))
        printStatistic(cell, 
                        path[cell]['inputPin'], \
                        cin, \
                        outCapList[cell], \
                        para, \
                        logic, \
                        be , \
                        cout/cin
                    )
        delay += (getLogicalEffort(cell) * cout/cin) * 14.7722 + parasitic_delay * 34.25
    print("Path " + str(j) + " before Sizing: " + str(delay) + " ps")
    print("After Optimize:")
    printTitle(1)
    delay = 0
    for i in range(len(path)): 
        cell = list(path)[i]
        if i == len(path)-1:
            cout = outCapList[cell]
        else:
            nextCell = list(path)[i+1]
            cout = outCapList[cell] - float(cellList[blockList[nextCell]['type']][path[nextCell]['inputPin']]['capacitance']) + capTransList[nextCell]
        cin = capTransList[cell]
        printStatistic(cell, 
                        path[cell]['inputPin'], \
                        cin, \
                        cout, \
                        float(int(subckt[path[cell]['type']]['pmos']) + int(subckt[path[cell]['type']]['nmos'])) / 3, \
                        getLogicalEffort(cell), \
                        getPathBranchingEffort2(cell, path, outCapList, cout), \
                        cout/cin, \
                        1
                        )
        delay += (getLogicalEffort(cell) * cout/cin) * 14.7722 + parasitic_delay * 34.25
    print("Path " + str(j) + " after Sizing: " + str(delay) + " ps")
    print(("Path " + str(j)).ljust(9) + " process done !")

