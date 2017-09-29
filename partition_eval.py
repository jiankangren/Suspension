from __future__ import division
from collections import OrderedDict
import partition_ILP as multi
import combo_ILP as combo
import STPartition as STP
import generator
import sys
import math
import numpy as np
from scipy.stats.mstats import gmean
from miscs import *

def main():
    args = sys.argv
    if len(args) < 5:
            print "Usage: python partition_eval.py [debug] [# of sets] [generate/load] [stype] [btype]"
            return -1 # no input

    debug = int (args[1])
    if debug == 0:
        tasksets_amount = int (args[2])
        mode = int(args[3]) # 0 = generate, 1 = directly use the inputs
        stype = args[4] # S, M, L
        btype = args[5] # {1, 2, 3} as {0.2, 0.5, 0.75} * minimum period
        #if btype == 0, it is the preemptive test
        inputfiles_amount = 1 # n for distribution
        tasksets_amount = int(math.ceil(tasksets_amount / inputfiles_amount))

        dist_utilizations = OrderedDict()
        dist_utilizations['10Tasks'] = 10
        dist_utilizations['20Tasks'] = 20
        dist_utilizations['30Tasks'] = 30
        dist_utilizations['40Tasks'] = 40

        idx = 0
        perAmount = [[] for i in range(len(dist_utilizations.items()))]
        for set_name, amount in dist_utilizations.items():
            for uti in range(int(100/10*amount), int(450/10*amount)+1, 5*amount):
            #for uti in range(int(450/10*amount), int(450/10*amount)+1, 5*amount):
                if idx == 2 and uti >= 1350: # 30 tasks
                    continue
                if idx == 3 and uti >= 1600: # 40 tasks
                    continue

                if mode == 0:
                    if stype == 'S':
                        tasksets = [generator.taskGeneration(amount, uti, 'S', 0, btype) for n in range(tasksets_amount)]
                        np.save ('input/'+str(set_name)+'_'+str(uti)+'_S_'+str(btype), tasksets)

                    elif stype == 'M':
                        tasksets = [generator.taskGeneration(amount, uti, 'M', 0, btype) for n in range(tasksets_amount)]
                        np.save ('input/'+str(set_name)+'_'+str(uti)+'_M_'+str(btype), tasksets)

                    elif stype == 'L':
                        tasksets = [generator.taskGeneration(amount, uti, 'L', 0, btype) for n in range(tasksets_amount)]
                        np.save ('input/'+str(set_name)+'_'+str(uti)+'_L_'+str(btype), tasksets)
                else:
                    pass
                    #TODO check if the inputs are there.
                perAmount[idx].append('input/'+str(set_name)+'_'+str(uti)+'_'+str(stype)+'_'+str(btype)+'.npy')
            idx+=1
        print perAmount

        if mode == 1:
            gRes=[[] for i in range(17)] # 17 methods
            for idx, filenames  in enumerate(perAmount):
                fileEx = 'Exceptions-tasks'+repr((1+idx)*10)+'_stype'+str(stype)+'_btype'+str(btype)
                fileB = 'Results-tasks'+repr((1+idx)*10)+'_stype'+str(stype)+'_btype'+str(btype)

                #fileEx = 'Exceptions-tasks'+repr((1+idx)*30)+'_stype'+repr(stype)+'_group'+repr(group)
                #fileB = 'Results-tasks'+repr((1+idx)*30)+'_stype'+repr(stype)+'_group'+repr(group)
                file_Ex = open('output/'+fileEx + '.txt', "w")
                file_B = open('output/'+fileB + '.txt', "w")
                for filename in filenames:
                    file_B.write(filename+'\n')
                    file_Ex.write(filename+'\n')
                    tasksets = np.load(filename)
                    for taskset in tasksets:
                        if idx == 2 or idx == 3:
                            res = test(taskset, debug, 1, btype)
                        else:
                            res = test(taskset, debug, 0, btype)

                        file_B.write('[ILPcarry, ILPblock, ILPjit, Inflation, ILPbaseline, Combo, TDA, TDAcarry, TDAblock, TDAjit, TDAjitblock, TDAmix, CTbaseline, CTcarry, CTblock, CTjit, CTmix]\n')
                        file_B.write(str(res)+'\n')
                        for ind, j in enumerate(res):
                            if j == -1:
                                #file_B.write('Infeasible in ILP \n')
                                file_Ex.write('Infeasible in ILP \n')
                                file_Ex.write(str(taskset)+'\n')
                                file_Ex.write(str(res)+'\n')
                                gRes[ind].append(len(taskset))
                            elif j == -2:
                                #file_B.write('ILP pops out an uncatched status \n')
                                file_Ex.write('ILP pops out an uncatched status \n')
                                file_Ex.write(str(taskset)+'\n')
                                file_Ex.write(str(res)+'\n')
                                gRes[ind].append(len(taskset))
                            elif j == -3:
                                #file_B.write('Infeasible in the double checking \n')
                                file_Ex.write('Infeasible in the double checking \n')
                                file_Ex.write(str(taskset)+'\n')
                                file_Ex.write(str(res)+'\n')
                                gRes[ind].append(len(taskset))
                            else:
                                gRes[ind].append(j)
                    # Way of present
                    result = []
                    for i in gRes:
                        result.append(gmean(i))
                    file_B.write('Gmean: \n')
                    file_B.write(str(result)+'\n')
                file_B.close()
                file_Ex.close()
        if mode == 2:
            gRes=[[] for i in range(17)] # 17 methods
            for idx, filenames  in enumerate(perAmount):
                if idx == 2: #print for 30 tasks
                    fileA = 'DEtasks'+repr((1+idx)*10)+'_stype'+repr(stype)+'_btype'+repr(btype)
                    file = open('output/'+fileA + '.txt', "w")
                    for filename in filenames:
                        file.write(filename+'\n')
                        tasksets = np.load(filename)
                        for taskset in tasksets:
                            file.write(str(taskset)+'\n')
                            sumUt = 0.0
                            sumUs = 0.0
                            for i in taskset:
                                sumUt += utili(i)
                                sumUs += utiliAddE(i)
                            file.write('total utili:'+str(sumUt)+'\n')
                            file.write('total utili+exclusive:'+str(sumUs)+'\n')
                        file.write('\n')
                    file.close()

    else:
        # DEBUG
        # generate some taskset, third argument is for sstype setting as PASS {S, M, L}
        taskset = generator.taskGeneration(4, 300, 'S', 0, 1)
        #test(taskset, debug, 1)

def test(taskset, debug, flag, btype):
    # taskset, num of procs
    obj = []
    if debug == 1:
        obj.append(multi.partition(taskset, 'ilpbaseline'))
        print "DEBUG MODE:"
    else:
        # ILP Tests
        if flag == 0:
            obj.append(multi.partition(taskset, 'carryin'))
            if btype != "N":
                obj.append(len(taskset))
            else:
                obj.append(multi.partition(taskset, 'blocking'))
            obj.append(multi.partition(taskset, 'k2q'))
            obj.append(multi.partition(taskset, 'inflation'))
            obj.append(multi.partition(taskset, 'ilpbaseline'))
            obj.append(combo.partition(taskset))
        else:
            obj.append(len(taskset))
            obj.append(len(taskset))
            obj.append(len(taskset))
            obj.append(len(taskset))
            obj.append(len(taskset))
            obj.append(len(taskset))


        binpack = 'first'
        # Heuristic + TDA Tests
        objMap = STP.STPartition(taskset, 'tda', binpack)
        obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'carry', binpack)
        obj.append(objMap[0])
        if btype != "N":
            obj.append(len(taskset))
        else:
            objMap = STP.STPartition(taskset, 'block', binpack)
            obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'jit', binpack)
        obj.append(objMap[0])
        if btype != "N":
            obj.append(len(taskset))
        else:
            objMap = STP.STPartition(taskset, 'jitblock', binpack)
            obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'tdamix', binpack)
        obj.append(objMap[0])

        # Heuristic + Constant Time Tests
        objMap = STP.STPartition(taskset, 'CTbaseline', binpack)
        obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'CTcarry', binpack)
        obj.append(objMap[0])
        if btype != 'N':
            obj.append(len(taskset))
        else:
            objMap = STP.STPartition(taskset, 'CTblock', binpack)
            obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'CTjit', binpack)
        obj.append(objMap[0])
        objMap = STP.STPartition(taskset, 'CTmix', binpack)
        obj.append(objMap[0])

    # Show the results

    #print ''
    #print '[ILPcarry, ILPblock, ILPjit, Inflation, Combo, TDAcarry, TDAblock, TDAjit, TDAjitblock, TDAmix, CTcarry, CTblock, CTjit, CTmix]'
    #print obj
    return obj
if __name__ == "__main__":
    main()
