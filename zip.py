import gzip

size = 16384

with open('largefile', 'rb') as f_in:
    with gzip.open('largefile.gz', 'wb') as f_out:
        while (data := f_in.read(size)):
            f_out.write(data)

f_out.close()
