import random
from uuid import uuid4
from time import sleep
from sharq import SharQ
sq = SharQ('./sharq.conf')

while True:
    response = sq.dequeue(queue_type='sms')
    status = response.get('status', 'failure')
    if status == 'success':
        print(response)
        if bool(random.getrandbits(1)):
            response = sq.finish(queue_type='sms',
                    job_id=response['job_id'],
                    queue_id=response['queue_id'],
	    )
        print(response)
