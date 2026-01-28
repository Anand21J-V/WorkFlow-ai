import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
worker_class = "sync"
timeout = 300
accesslog = "-"
errorlog = "-"
loglevel = "info"
preload_app = False