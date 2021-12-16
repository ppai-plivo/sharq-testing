## SharQ Wishlist

### API to display size/length of a queue

Usecases:
* Display number of messages in queue in realtime via console.
* Estimate how long it would take for messages to be dequeued (we already have interval).

### Message unit ratelimiting

Currently ratelimiting is applied per message regardless of no. of units. This can be changed/tweaked to be applied to message units. But why? The industry has supported 1 message per second for long codes however Plivo has historically supported 1 message per 4 seconds for long code. I was told by Haiku, the then PM that this extra buffer was to take care of carriers applying ratelimits on a per unit basis.
