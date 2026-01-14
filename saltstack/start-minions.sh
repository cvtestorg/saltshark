#!/bin/bash
set -e
NUM_MINIONS=${1:-3}
echo "Starting $NUM_MINIONS Salt Minions..."
if ! command -v salt-minion &> /dev/null; then
    echo "Error: salt-minion not found."
    exit 1
fi
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Must run as root"
    exit 1
fi
mkdir -p /etc/salt/minion.d
cp minion/minion.conf /etc/salt/minion.d/
for i in $(seq 1 $NUM_MINIONS); do
    MINION_ID="minion-$i"
    MINION_CONFIG_DIR="/etc/salt/minion-$i"
    echo "Starting $MINION_ID..."
    mkdir -p "$MINION_CONFIG_DIR/minion.d" "$MINION_CONFIG_DIR/pki" "$MINION_CONFIG_DIR/cache"
    cp minion/minion.conf "$MINION_CONFIG_DIR/minion.d/"
    cat > "$MINION_CONFIG_DIR/minion.d/id.conf" <<IDCONF
id: $MINION_ID
pki_dir: $MINION_CONFIG_DIR/pki
cachedir: $MINION_CONFIG_DIR/cache
IDCONF
    salt-minion -c "$MINION_CONFIG_DIR" -d
    sleep 1
done
echo "✅ Started $NUM_MINIONS minions!"
