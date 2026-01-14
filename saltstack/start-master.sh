#!/bin/bash
set -e
echo "Starting Salt Master..."
if ! command -v salt-master &> /dev/null; then
    echo "Error: salt-master not found."
    exit 1
fi
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Must run as root"
    exit 1
fi
mkdir -p /etc/salt/master.d /etc/salt/api.d /srv/salt /srv/pillar
cp master/master.conf /etc/salt/master.d/
cp api/api.conf /etc/salt/api.d/
if ! id "saltapi" &>/dev/null; then
    useradd -m -s /bin/bash saltapi
    echo "saltapi:saltapi" | chpasswd
fi
salt-master -d
sleep 3
salt-api -d
echo "✅ Salt Master and API started!"
echo "API: http://localhost:8000 (saltapi/saltapi)"
