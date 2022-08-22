# Example Python program to gzip a large file

This demo illustrates how to improve performance of libz for a Python application.

It has been prepared for an AWS EC2 instance running AWS Graviton processors.

### Start an AWS EC2 instance with Graviton

Launch a c6g.medium instance type running Ubuntu 22.04 

Set up ssh access to the machine

### Setup 

Note the default libz package is zlib 1.2.11

Set the default python to be python3.

```console
sudo apt install python-is-python3 -y
```

Install perf:

```console
sudo apt install linux-tools-common linux-tools-generic linux-tools-`uname -r` -y
sudo sh -c "echo '1' > /proc/sys/kernel/perf_event_paranoid"
```

### Create a large file

```console
dd if=/dev/zero of=largefile count=1M bs=1024
```

### Compress the file

```console
perf stat python ./zip.py
```

Note the seconds of elapsed time.

### Generage the flame graph

```console
perf record -F 99 -g python ./zip.py
perf report
git clone https://github.com/brendangregg/FlameGraph
perf script | ./FlameGraph/stackcollapse-perf.pl > out.perf-folded && ./FlameGraph/flamegraph.pl out.perf-folded > flamegraph1.svg
```

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
cd zlib && mkdir ~/zlib && ./configure --prefix=$HOME/zlib
make && make install && cd ~/zip
```
Confirm new libz has crc instructions.

```console
objdump -d ~/zlib/lib/libz.so | awk -F " "  '{print $3}' | grep crc32 | wc -l
```

### Run the python program again

```console
LD_PRELOAD=~/zlib/lib/libz.so  perf stat python ./zip.py
```

Note the new seconds of elapsed time.

```console
perf record -F 99 -g python ./zip.py
perf script | ./FlameGraph/stackcollapse-perf.pl > out.perf-folded && ./FlameGraph/flamegraph.pl out.perf-folded > flamegraph2.svg
```

