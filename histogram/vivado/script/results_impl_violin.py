#!/usr/bin/env python3
import itertools
import os, sys
import glob
import re
import numpy as np
import xml.etree.ElementTree as ET

# ***************************************************************************
# Knobs
# ***********
blockdim_x =[1,2,4,8]
blockdim_y =[1,2,4,8]
unroll_dct=[1,2,4,8]
unroll_width=[1,2,4,8]
unroll_height=[1,2,4,8]
array_partition=[1,2,4,8]


allCombinations = list(itertools.product(
    blockdim_x,
    blockdim_y,
    unroll_dct,
    unroll_width,
    unroll_height,
    array_partition))



# ***************************************************************************


def parse_resources(resources_node):
    tags = ['BRAM_18K','DSP48E','FF','LUT']
    resources = [ resources_node.find(t).text for t in tags ]
    return list(map(int, resources))

def parse_xml(filename1,filename2):
    tree = ET.parse(filename1)
    root = tree.getroot()
    print(filename1)
    #resources_node       = root.find('AreaEstimates/Resources')
    #avail_resources_node = root.find('AreaEstimates/AvailableResources')
    est_clk_period = root.find('TimingReport/AchievedClockPeriod').text
    slices=root.find('AreaReport/Resources/CLB').text
    slices=int(slices)
    lut = int(root.find('AreaReport/Resources/LUT').text)
    ff = int(root.find('AreaReport/Resources/FF').text)
    dsp = int(root.find('AreaReport/Resources/DSP').text)
    bram = int(root.find('AreaReport/Resources/BRAM').text)
    tree=ET.parse(filename2)
    root=tree.getroot()
    avg_latency = root.find('PerformanceEstimates/SummaryOfOverallLatency/Average-caseLatency').text
    throughput="{0:.6f}".format(((int(avg_latency)*float(est_clk_period))/1000000000))
    throughput=1.0/float(throughput)
    #resources       = parse_resources(resources_node)
    #avail_resources = parse_resources(avail_resources_node)
    
    #resources_util = np.divide(resources, avail_resources)*100
    #for i in range(4):
        #resources_util[i]="{0:.2f}".format(resources_util[i])
    return slices,lut,ff,dsp,bram,throughput

def removeCombinations(combs):

    finalList = []

    for c in combs:
        copyit = True
	
        #if c[2]>c[0] or c[2]>c[1]:
            #copyit =False

        if copyit:
            finalList.append(c)

    return finalList


def main():

    #finalCombinations = removeCombinations(allCombinations)
    file1=open('vivado_histogram_violin.csv','w')
    file1.write("Parameter"+","+"Throughput_Value"+","+"Tool"+","+"Resource_Type"+","+"Resource_Value"+","+"Parameter3"+","+"FF_Value"+","+"Flow"+"\n")
    for d in sorted(glob.glob('impl_reports/histogram_main_export*.xml')):
        m = re.search('histogram_main_export(\d+)', d)
        num = m.group(1)
        synth_path=os.path.join('syn_reports/csynth'+num+'.xml')
        try:
            slices,lut,ff,dsp,bram,lat=parse_xml(d,synth_path)
            if slices==0:
                pass
            else:
                file1.write("Throughput"+","+str(lat)+","+"vivado"+","+"CLB"+","+str(slices)+","+"FF"+","+str(ff)+","+"None"+"\n")
                file1.write("Throughput"+","+str(lat)+","+"vivado"+","+"LUT"+","+str(lut)+","+"FF"+","+str(ff)+","+"None"+"\n")
                file1.write("Throughput"+","+str(lat)+","+"vivado"+","+"FF"+","+str(ff)+","+"FF"+","+str(ff)+","+"None"+"\n")
                file1.write("Throughput"+","+str(lat)+","+"vivado"+","+"DSP"+","+str(dsp)+","+"FF"+","+str(ff)+","+"None"+"\n")
                file1.write("Throughput"+","+str(lat)+","+"vivado"+","+"BRAM"+","+str(bram)+","+"FF"+","+str(ff)+","+"None"+"\n")
        except:
            pass
    file1.close()
if __name__ == "__main__":
    main()
        
