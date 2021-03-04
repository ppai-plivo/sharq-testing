from uuid import uuid4
from time import sleep
from sharq import SharQ
sq = SharQ('./sharq.conf')

count = 0
while True:
    resp = sq.enqueue(job_id=str(uuid4()),
            payload={'a': 'b'},
            interval=10,  # in milliseconds.
            queue_id='user001',
            queue_type='sms'
    )
    sleep(0.1)
    count = count + 1
    if count > 100:
        break
