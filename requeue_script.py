from uuid import uuid4
from time import sleep
from sharq import SharQ

sq = SharQ('./sharq.conf')

while True:
    response = sq.requeue()
    if response is not None:
        print(response)
    sleep(0.1)
