import signal
import threading
from time import sleep
from sharq import SharQ


THREAD_COUNT = 1
REQUEUE_INTERVAL = 5
STOP_THREADS = False


def requeue_worker(worker_id):
    sq = SharQ('./sharq.conf')
    while STOP_THREADS is False:
        response = sq.requeue()
        if response is not None:
            print(response)
        sleep(REQUEUE_INTERVAL)
    print("thread-{}: exiting".format(worker_id))


if __name__ == '__main__':
    threads = [threading.Thread(target=requeue_worker,
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
