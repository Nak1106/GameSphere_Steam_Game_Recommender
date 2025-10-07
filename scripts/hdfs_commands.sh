#!/bin/bash

# GameSphere HDFS Commands Reference
# All essential HDFS commands for data management

# =============================================================================
# HDFS CLUSTER MANAGEMENT
# =============================================================================

# Start HDFS services
echo "=== HDFS Cluster Management ==="
echo "Start HDFS:"
echo "  \$HADOOP_HOME/sbin/start-dfs.sh"
echo ""

echo "Stop HDFS:"
echo "  \$HADOOP_HOME/sbin/stop-dfs.sh"
echo ""

echo "Check HDFS status:"
echo "  jps | grep -E '(NameNode|DataNode)'"
echo ""

echo "Format namenode (ONLY if needed):"
echo "  \$HADOOP_HOME/bin/hdfs namenode -format -force"
echo ""

# =============================================================================
# DIRECTORY OPERATIONS
# =============================================================================

echo "=== Directory Operations ==="
echo "List HDFS directories:"
echo "  hdfs dfs -ls /"
echo "  hdfs dfs -ls /project/"
echo ""

echo "Create directories:"
echo "  hdfs dfs -mkdir -p /project/raw"
echo "  hdfs dfs -mkdir -p /project/processed"
echo "  hdfs dfs -mkdir -p /project/data/processed"
echo "  hdfs dfs -mkdir -p /project/outputs"
echo "  hdfs dfs -mkdir -p /project/data/mappings"
echo ""

echo "Remove directories:"
echo "  hdfs dfs -rm -r /project/raw"
echo ""

# =============================================================================
# FILE OPERATIONS
# =============================================================================

echo "=== File Operations ==="
echo "Upload raw data to HDFS:"
echo "  hdfs dfs -put data/raw_data/steam_reviews.csv /project/raw/"
echo ""

echo "Download data from HDFS:"
echo "  hdfs dfs -get /project/processed/steam_review_english.parquet ./local_data/"
echo ""

echo "Copy files within HDFS:"
echo "  hdfs dfs -cp /project/raw/steam_reviews.csv /project/backup/"
echo ""

echo "View file contents (first 10 lines):"
echo "  hdfs dfs -head /project/raw/steam_reviews.csv"
echo ""

echo "Check file size:"
echo "  hdfs dfs -du -h /project/raw/"
echo ""

echo "Remove files:"
echo "  hdfs dfs -rm /project/raw/steam_reviews.csv"
echo ""

# =============================================================================
# MONITORING & DEBUGGING
# =============================================================================

echo "=== Monitoring & Debugging ==="
echo "Check HDFS health:"
echo "  hdfs dfsadmin -report"
echo ""

echo "Check disk usage:"
echo "  hdfs dfs -df -h"
echo ""

echo "Safe mode operations:"
echo "  hdfs dfsadmin -safemode get"
echo "  hdfs dfsadmin -safemode leave"
echo ""

echo "View HDFS Web UI:"
echo "  http://localhost:9870"
echo ""

# =============================================================================
# GAMEOSPHERE SPECIFIC COMMANDS
# =============================================================================

echo "=== GameSphere Specific Commands ==="
echo "Setup complete HDFS structure:"
echo "  hdfs dfs -mkdir -p /project/{raw,processed,data/processed,outputs,data/mappings}"
echo ""

echo "Upload GameSphere raw data:"
echo "  hdfs dfs -put data/raw_data/steam_reviews.csv /project/raw/"
echo ""

echo "Check pipeline outputs:"
echo "  hdfs dfs -ls /project/processed/"
echo "  hdfs dfs -ls /project/data/processed/"
echo "  hdfs dfs -ls /project/outputs/"
echo ""

echo "View processed data samples:"
echo "  hdfs dfs -head /project/processed/steam_review_english.parquet"
echo ""

# =============================================================================
# QUICK SETUP COMMANDS
# =============================================================================

echo "=== Quick Setup (Run these in order) ==="
echo "1. Start HDFS:"
echo "   \$HADOOP_HOME/sbin/start-dfs.sh"
echo ""
echo "2. Create directories:"
echo "   hdfs dfs -mkdir -p /project/{raw,processed,data/processed,outputs,data/mappings}"
echo ""
echo "3. Upload raw data:"
echo "   hdfs dfs -put data/raw_data/steam_reviews.csv /project/raw/"
echo ""
echo "4. Verify setup:"
echo "   hdfs dfs -ls /project/raw/"
echo ""

# =============================================================================
# EXECUTABLE COMMANDS (Uncomment to run)
# =============================================================================

# Uncomment the following lines to execute commands directly:

# echo "Executing HDFS setup commands..."

# # Set environment variables
# export HADOOP_HOME=~/Hadoop/hadoop-3.4.1
# export JAVA_HOME=/opt/homebrew/opt/openjdk@11
# export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

# # Start HDFS (if not running)
# echo "Starting HDFS..."
# $HADOOP_HOME/sbin/start-dfs.sh

# # Wait for services to start
# sleep 10

# # Create directory structure
# echo "Creating HDFS directories..."
# hdfs dfs -mkdir -p /project/{raw,processed,data/processed,outputs,data/mappings}

# # Upload raw data
# echo "Uploading raw data..."
# hdfs dfs -put data/raw_data/steam_reviews.csv /project/raw/

# # Verify setup
# echo "Verifying HDFS setup..."
# hdfs dfs -ls /project/
# hdfs dfs -ls /project/raw/

echo ""
echo "=== HDFS Commands Reference Complete ==="
echo "To execute setup commands, uncomment the bottom section of this script"
