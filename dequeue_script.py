import random
import signal
import threading
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
from sharq import SharQ

default_job_requeue_limit = 3  # must be same value as in sharq.conf
job_expire_interval = 10000    # must be same value as in sharq.conf

STOP_THREADS = False
THREAD_COUNT = 4

deqs = defaultdict(int)
acks = defaultdict(int)
no_acks = defaultdict(int)
deq_time = defaultdict(list)


def diff_in_percent(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0.0


def dequeue_worker(worker_id):
    global STOP_THREADS, deqs, acks, no_acks

    sq = SharQ('./sharq.conf')

    while STOP_THREADS is False:
        response = sq.dequeue(queue_type='sms')
        if len(response) <= 1:
            continue
        status = response.get('status', 'failure')
        if status == 'success':
            # make a note of when a job was dequeued
            deq_time[response['job_id']].append(datetime.now())

            # increment dequeue counter for the job
            deqs[response['job_id']] += 1

            # randomly call finish or not
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
        assert(value > 0 and value <= default_job_requeue_limit + 1)

    # verify that items that have been ACKd do not appear again
    # and have appeared exactly once.
    for key, value in acks.items():
        assert(value == 1)

    # verify that items that have not been ackd, have been dequeued
    # more than once but less than the requeue limit
    for key, value in no_acks.items():
        assert(deqs[key] > 1 and deqs[key] <= (default_job_requeue_limit + 1))

    # verify that time between requeues is <= job_expire_interval
    print("\nTime between dequeues:\n")
    for key, value in deq_time.items():
        if len(value) <= 1:
            # dequeued just once, nothing to verify
            continue
        for i in range(len(value)):
            if i+1 >= len(value):
                break
            td = value[i+1] - value[i]
            td_in_ms = td / timedelta(milliseconds=1)
            print(int(td_in_ms), round(diff_in_percent(td_in_ms, job_expire_interval), 2), end=" ")
            if td_in_ms < job_expire_interval:
                assert(diff_in_percent(td_in_ms, job_expire_interval) <= 2.0)
            elif td_in_ms > job_expire_interval:
                assert(diff_in_percent(td_in_ms, job_expire_interval) <= 75.0)
