from sharq import SharQ

sq = SharQ('./sharq.conf')

for i in range(1000):
    resp = sq.enqueue(job_id=str(i),
                      payload={'a': 'b'},
                      interval=10,  # in milliseconds.
                      queue_id='user001',
                      queue_type='sms')
