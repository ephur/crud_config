import multiprocessing

bind = "127.0.0.1:5001"
workers = multiprocessing.cpu_count() + 1
worker_class = 'sync'
backlog = 16384
