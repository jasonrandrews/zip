# Example Python program to gzip a large file

This demo illustrates how to improve performance of libz for a Python application.

It has been prepared for an AWS EC2 instance running AWS Graviton processors.

### Start an AWS EC2 instance with Graviton

Launch a t4g.small instance type running Ubuntu 22.04 

t4g.small has a free trial running until December 31, 2022

Connect to the EC2 instance using ssh or another method. Refer to the [AWS documenation for more details](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html)

### Setup 

Note the default libz package is zlib 1.2.11

Set the default python to be python3

```console
sudo apt update
sudo apt install make gcc -y
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

Generate the flame graph

```console
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
pushd zlib && mkdir ~/zlib && ./configure --prefix=$HOME/zlib
make && make install
popd
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

