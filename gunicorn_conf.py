"""
Gunicorn configuration file for running FastAPI applications.
This uses the Uvicorn worker class to properly handle ASGI.
"""
import multiprocessing

# Use the Uvicorn worker for ASGI compatibility with FastAPI
worker_class = "uvicorn.workers.UvicornWorker"

# Bind to all network interfaces on port 5000
bind = "0.0.0.0:5000"

# Set the number of workers based on the CPU cores
workers = multiprocessing.cpu_count() * 2 + 1

# Enable reloading when files change
reload = True

# Log level
loglevel = "debug"