import random
import signal
import threading
from collections import defaultdict, OrderedDict
from sharq import SharQ


STOP_THREADS = False
THREAD_COUNT = 4
default_job_requeue_limit = 1

deqs = defaultdict(int)
acks = defaultdict(int)
no_acks = defaultdict(int)


def dequeue_worker(worker_id):
    global STOP_THREADS, deqs, acks, no_acks

    sq = SharQ('./sharq.conf')

    while STOP_THREADS is False:
        response = sq.dequeue(queue_type='sms')
        if len(response) <= 1:
            continue
        status = response.get('status', 'failure')
        if status == 'success':
            deqs[response['job_id']] += 1
            if bool(random.getrandbits(1)):
                sq.finish(queue_type='sms',
                          job_id=response['job_id'],
                          queue_id=response['queue_id'])
                acks[response['job_id']] += 1
            else:
                no_acks[response['job_id']] += 1

    print("thread-{}: exiting".format(worker_id))


if __name__ == '__main__':
    threads = [threading.Thread(target=dequeue_worker,
                                args=(x,),
                                name=str(x)) for x in range(THREAD_COUNT)]

    for t in threads:
        t.start()

    def signal_handler(sig, frame):
        print("got signal: {}\n".format(signal.strsignal(sig)))
        global STOP_THREADS
        STOP_THREADS = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for t in threads:
        t.join()
    print("all threads ended")

    print("\nDequeued:\n",
          OrderedDict(sorted(deqs.items(), key=lambda x: int(x[0]))))
    print("\nAcked:\n",
          OrderedDict(sorted(acks.items(), key=lambda x: int(x[0]))))
    print("\nNot Acked:\n",
          OrderedDict(sorted(no_acks.items(), key=lambda x: int(x[0]))))

    # verify that total dequeues do not exceed the limit
    for key, value in deqs.items():
        assert(value == (default_job_requeue_limit + 1) or value == 1)

    # verify that items that have been ACKd do not appear again
    # and have appeared exactly once.
    for key, value in acks.items():
        assert(value == 1)

    # verify that items that have not been ackd, have been dequeued
    # more than once but less than the requeue limit
    for key, value in no_acks.items():
        assert(deqs[key] > 1 and deqs[key] <= (default_job_requeue_limit + 1))
