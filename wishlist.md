## SharQ Wishlist

### API to display size/length of a queue

Usecases:
* Display number of messages in queue in realtime via console.
* Estimate how long it would take for messages to be dequeued (we already have interval).

### Batch enqueue

Usecase: Request to send a SMS towards multiple destinations can timeout as Plivo API is basically calling enqueue in a loop for every destination number. This means that the customer/client would get a 5xx response despite a part of messages being successfully queued. This makes the API operation inconsistent.
