k6 run --vus 1 --duration 1m --out influxdb=http://138.246.234.122:8086/myk6db script1.js
k6 run --vus 2 --duration 1m --out influxdb=http://138.246.234.122:8086/myk6db script1.js
k6 run --vus 3 --duration 1m --out influxdb=http://138.246.234.122:8086/myk6db script1.js
k6 run --vus 4 --duration 1m --out influxdb=http://138.246.234.122:8086/myk6db script1.js
