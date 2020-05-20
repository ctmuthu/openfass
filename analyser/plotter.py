import matplotlib.pyplot as plt

def plot(dt,value):
    plt.plot(dt,value)
    plt.show()

def multiplot(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime, replicaDT, replicas):
    #print(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime)
    
    plt.figure()

    plt.subplot(331)
    plt.plot(cpuDT, cpuSec)
    plt.ylabel('% CPU Utilization')
    plt.grid(True)

    plt.subplot(332)
    plt.plot(memDT, memUsage)
    plt.ylabel('% Memory utilization')
    plt.grid(True)

    plt.subplot(333)
    plt.plot(reqDT, reqCount)
    plt.ylabel('Function requests per second')
    plt.grid(True)

    plt.subplot(334)
    plt.plot(res200DT, res200Count)
    plt.ylabel('Successful Function invocation')
    plt.grid(True)

    plt.subplot(335)
    plt.plot(res502DT, res502Count)
    plt.ylabel('Unsuccessful function invocations')
    plt.grid(True)

    plt.subplot(336)
    plt.plot(resDT, resTime)
    plt.ylabel('Average function execution time')
    plt.grid(True)

    # reqCount_modified = reqCount[:len(resTime)]

    plt.subplot(337)
    plt.plot(replicaDT, replicas)
    plt.ylabel('Number of Replicas')
    plt.grid(True)

    # plt.subplot(337)
    # plt.plot(res502Count, res200Count)
    # plt.ylabel('Average function execution time from openfaas')
    # plt.grid(True)

    plt.savefig('./analyser/graph.png')
    plt.show()