from dask.distributed import Client, progress
import dask.bag as db
client = Client(scheduler_file='scheduler.json')
b = db.read_text('file:///work/logiciels/rh7/Python/3.5.2/lib/python3.5/*.py')
wordcount = b.str.split().flatten().frequencies().topk(10, lambda x: x[1])
future = client.compute(wordcount)
print(future)
progress(future)

results = client.gather(future)
print(results)


