#!/bin/bash
# Start Waldo Commander with ROS 2 environment
# Use this script for ROS 2 integration testing instead of running waldo-commander directly.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

cd "$SCRIPT_DIR"

# Kill any stale parol6 server holding port 5001
pkill -f "parol6.server" 2>/dev/null
pkill -f "waldo-commander" 2>/dev/null
sleep 1

PAROL6_FAKE_SERIAL=1 WALDO_SKIP_ENVELOPE=1 waldo_env/bin/waldo-commander --log-level INFO "$@"
