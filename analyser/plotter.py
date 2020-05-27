import matplotlib.pyplot as plt

def plot(dt,value):
    plt.plot(dt,value)
    plt.show()

def multiplot(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime):
    #print(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime)
    
    plt.figure()

    plt.subplot(321)
    plt.plot(cpuDT, cpuSec)
    plt.ylabel('% CPU Utilization')
    plt.grid(True)

    plt.subplot(322)
    plt.plot(memDT, memUsage)
    plt.ylabel('% Memory utilization')
    plt.grid(True)

    plt.subplot(323)
    plt.plot(reqDT, reqCount)
    plt.ylabel('Function requests \n per second')
    plt.grid(True)

    plt.subplot(324)
    plt.plot(res200DT, res200Count)
    plt.ylabel('Successful Function \n invocation')
    plt.grid(True)

    plt.subplot(325)
    plt.plot(res502DT, res502Count)
    plt.ylabel('Unsuccessful function \n invocations')
    plt.grid(True)

    plt.subplot(326)
    plt.plot(resDT, resTime)
    plt.ylabel('Average function \n execution time')
    plt.grid(True)

    plt.savefig('./analyser/graph.png')
    plt.show()