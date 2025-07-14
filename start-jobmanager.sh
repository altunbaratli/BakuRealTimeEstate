#!/bin/bash

# Start the Flink JobManager in background
bin/jobmanager.sh start cluster

# Optional: Wait to make sure JM is ready
sleep 10

# Submit the PyFlink job
bin/flink run -py /opt/flink_jobs/flink_job.py

# Keep container alive (so Docker doesn't stop the container)
tail -f /dev/null