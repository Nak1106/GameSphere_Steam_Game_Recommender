#!/bin/bash

# GameSphere Steam Recommender - macOS Bootstrap Script
# This script sets up the complete environment for GameSphere on macOS (Apple Silicon)

set -e  # Exit on any error

echo "🚀 Starting GameSphere macOS Bootstrap..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    print_status "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    print_status "Homebrew already installed ✓"
fi

# Install required packages
print_status "Installing required packages via Homebrew..."
brew install openjdk@11 python@3.10 wget git

# Set up directories
print_status "Setting up Hadoop and Spark directories..."
mkdir -p ~/Hadoop ~/Spark

# Download and install Hadoop 3.4.1
HADOOP_VERSION="3.4.1"
HADOOP_DIR="$HOME/Hadoop/hadoop-$HADOOP_VERSION"

if [ ! -d "$HADOOP_DIR" ]; then
    print_status "Downloading and installing Hadoop $HADOOP_VERSION..."
    cd ~/Hadoop
    wget -q "https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz"
    tar -xzf "hadoop-$HADOOP_VERSION.tar.gz"
    rm "hadoop-$HADOOP_VERSION.tar.gz"
    print_status "Hadoop installed to $HADOOP_DIR ✓"
else
    print_status "Hadoop already installed ✓"
fi

# Download and install Spark 3.5.3
SPARK_VERSION="3.5.3"
HADOOP_SPARK_VERSION="3"
SPARK_DIR="$HOME/Spark/spark-$SPARK_VERSION"

if [ ! -d "$SPARK_DIR" ]; then
    print_status "Downloading and installing Spark $SPARK_VERSION..."
    cd ~/Spark
    wget -q "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_SPARK_VERSION.tgz"
    tar -xzf "spark-$SPARK_VERSION-bin-hadoop$HADOOP_SPARK_VERSION.tgz"
    mv "spark-$SPARK_VERSION-bin-hadoop$HADOOP_SPARK_VERSION" "spark-$SPARK_VERSION"
    rm "spark-$SPARK_VERSION-bin-hadoop$HADOOP_SPARK_VERSION.tgz"
    print_status "Spark installed to $SPARK_DIR ✓"
else
    print_status "Spark already installed ✓"
fi

# Update ~/.zshrc with environment variables
print_status "Updating ~/.zshrc with GameSphere environment variables..."

# Remove existing GameSphere env block if it exists
sed -i '' '/# GameSphere env/,/^$/d' ~/.zshrc 2>/dev/null || true

# Add new GameSphere env block
cat >> ~/.zshrc << 'EOF'

# GameSphere env
export JAVA_HOME=/opt/homebrew/opt/openjdk@11
export PATH="$JAVA_HOME/bin:$PATH"
export HADOOP_HOME=~/Hadoop/hadoop-3.4.1
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_HOME=~/Spark/spark-3.5.3
export PYSPARK_PYTHON=python3
export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

EOF

# Source the updated .zshrc
source ~/.zshrc

# Create Hadoop configuration files
print_status "Creating Hadoop configuration files..."

# Ensure HADOOP_CONF_DIR exists
mkdir -p "$HADOOP_HOME/etc/hadoop"

# Create core-site.xml
cat > "$HADOOP_HOME/etc/hadoop/core-site.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

# Create hdfs-site.xml
mkdir -p ~/Hadoop/hdfs-data/namenode ~/Hadoop/hdfs-data/datanode

cat > "$HADOOP_HOME/etc/hadoop/hdfs-site.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file://$HOME/Hadoop/hdfs-data/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file://$HOME/Hadoop/hdfs-data/datanode</value>
    </property>
    <property>
        <name>dfs.namenode.http-address</name>
        <value>localhost:9870</value>
    </property>
</configuration>
EOF

# Set JAVA_HOME in Hadoop env
echo "export JAVA_HOME=/opt/homebrew/opt/openjdk@11" >> "$HADOOP_HOME/etc/hadoop/hadoop-env.sh"

# Format namenode if not already formatted
if [ ! -d "$HOME/Hadoop/hdfs-data/namenode/current" ]; then
    print_status "Formatting HDFS namenode..."
    "$HADOOP_HOME/bin/hdfs" namenode -format -force
else
    print_status "HDFS namenode already formatted ✓"
fi

# Start HDFS
print_status "Starting HDFS..."
"$HADOOP_HOME/sbin/start-dfs.sh"

# Wait a moment for HDFS to start
sleep 5

# Create HDFS directories
print_status "Creating HDFS project directories..."
"$HADOOP_HOME/bin/hdfs" dfs -mkdir -p /project/raw /project/processed /project/data/processed /project/outputs /project/data/mappings

# Create Python virtual environment
print_status "Creating Python virtual environment..."
cd "$(dirname "$0")/.."  # Go to repo root
python3.10 -m venv .venv
source .venv/bin/activate

# Install Python requirements
if [ -f "requirements.txt" ]; then
    print_status "Installing Python requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Please create it and run 'pip install -r requirements.txt'"
fi

print_status "🎉 GameSphere macOS Bootstrap completed successfully!"
print_status ""
print_status "Next steps:"
print_status "1. Restart your terminal or run: source ~/.zshrc"
print_status "2. Activate Python environment: source .venv/bin/activate"
print_status "3. Put your raw data: make put-raw RAW=/path/to/steam_reviews.csv"
print_status "4. Run the pipeline: make run-clean run-sentiment run-als run-export"
print_status ""
print_status "Useful URLs:"
print_status "- HDFS Web UI: http://localhost:9870"
print_status "- Airflow UI: http://localhost:8080 (after 'make airflow-up')"
print_status "- MLflow UI: http://localhost:5000 (after 'make mlflow-ui')"
print_status "- Streamlit Dashboard: http://localhost:8501 (after 'make streamlit')"
