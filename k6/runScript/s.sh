#!/bin/sh

k6 run --out influxdb=http://138.246.234.122:8086/myk6db runScript/script1.js &
k6 run --out influxdb=http://138.246.234.122:8086/myk6db runScritp/script2.js
