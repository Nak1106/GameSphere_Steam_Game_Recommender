# GameSphere Airflow with Java and PySpark
FROM apache/airflow:2.9.2

# Switch to root to install system packages
USER root

# Install Java 17 and other system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME (detect architecture)
RUN if [ "$(uname -m)" = "aarch64" ]; then \
        echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64" >> /etc/environment; \
    else \
        echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> /etc/environment; \
    fi
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH=$PATH:$JAVA_HOME/bin

# Switch back to airflow user
USER airflow

# Copy requirements and install Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Set PySpark environment variables
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
