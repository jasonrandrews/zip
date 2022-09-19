# Example Python program to gzip a large file

This demo illustrates how to improve performance of libz for a Python application.

It has been prepared for an Arm Neoverse system running Ubuntu. 

It can be run on any cloud provider offering Arm instances, including AWS, Oracle Cloud, Google Cloud, or Microsoft Azure.

For more info about Arm cloud instances refer to [Getting Started with Arm Cloud instances](https://github.com/jasonrandrews/arm-cloud-info)

### Setup 

This example explains how to improve application performance using a custom version of zlib.

Set the default python to be python3

```console
sudo apt update
sudo apt install build-essential -y
sudo apt install python-is-python3 -y
```

Clone the project

```console
git clone https://github.com/jasonrandrews/zip.git
cd zip
```

Install perf

```console
sudo apt install linux-tools-common linux-tools-generic linux-tools-`uname -r` -y
```

```console
sudo sh -c "echo '1' > /proc/sys/kernel/perf_event_paranoid"
```

### Create a large file

```console
dd if=/dev/zero of=largefile count=1M bs=1024
```

### Compress the file

Run the python program to gzip the largefile

```console
perf stat python ./zip.py
```
Note the seconds of elapsed time

It's also possible to just time the execution.

```console
time python ./zip.py
```

### Generage the flame graph

```console
perf record -F 99 -g python ./zip.py
git clone https://github.com/brendangregg/FlameGraph
perf script | ./FlameGraph/stackcollapse-perf.pl > out.perf-folded && ./FlameGraph/flamegraph.pl out.perf-folded > flamegraph1.svg
```

Run perf report

```console
perf report
```

Note that the crc32 function is taking significant time

69.92%    68.27%  python   libz.so.1.2.11         [.] crc32

### Confirm crc32 is included in the processor flags

```console
lscpu | grep crc32
```

### Check if crc32 instuctions are used in libz

```console
objdump -d /usr/lib/aarch64-linux-gnu/libz.so.1 | awk -F" " '{print $3}' | grep crc32 | wc -l
```
If it returns 0 there are no crc instructions in libz. 

### Install Cloudflare libz

```console
git clone https://github.com/cloudflare/zlib.git
pushd zlib && mkdir ~/zlib && ./configure 
make && sudo make install
popd
```
Confirm new libz has crc instructions.

```console
objdump -d /usr/local/lib/libz.so | awk -F " "  '{print $3}' | grep crc32 | wc -l
```

### Run the python program again

```console
LD_PRELOAD=/usr/local/lib/libz.so  perf stat python ./zip.py
```

Note the new seconds of elapsed time.

```console
LD_PRELOAD=/usr/local/lib/libz.so perf perf record -F 99 -g python ./zip.py
perf script | ./FlameGraph/stackcollapse-perf.pl > out.perf-folded && ./FlameGraph/flamegraph.pl out.perf-folded > flamegraph2.svg
```

For more infomation refer to [Improve data compression performance on AWS Graviton processors](https://dev.to/aws-builders/improve-data-compression-performance-on-aws-graviton-processors-1pg0)
