#!/usr/bin/env bash
cd image
docker build -t anthonyrawlinsuom/dssh .
docker push anthonyrawlinsuom/dssh
cd ..