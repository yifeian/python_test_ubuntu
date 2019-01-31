from multiprocessing import Process, Queue

#queues:
def f(q):
    q.put([42,None,'hello'])
    q.put([43,None,'hello'])
    q.put([44,None,'hello'])

if __name__ == "__main__":
    q = Queue()
    p = Process(target=f,args=(q,))
    p.start()
    print(q.get())
    p.join()


