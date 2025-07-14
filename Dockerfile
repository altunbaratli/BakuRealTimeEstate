FROM flink:2.0.0

RUN apt-get update -y && \
    apt-get install -y \
      default-jdk \
      python3 \
      python3-dev \
      python3-pip \
      && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

RUN ln -s /usr/bin/python3 /usr/bin/python

# Install PyFlink
RUN pip3 install apache-flink==2.0.0

USER flink
RUN mkdir /opt/flink/usrlib
COPY flink_jobs/flink_job.py /opt/flink/usrlib/flink_job.py
COPY connectors/* /opt/flink/lib/