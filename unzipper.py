import sys, zipfile
from concurrent.futures import ProcessPoolExecutor

src, dst, n = sys.argv[1], sys.argv[2], int(sys.argv[3])

def work(names):
    with zipfile.ZipFile(src) as z:
        for name in names:
            z.extract(name, dst)

if __name__ == "__main__":
    with zipfile.ZipFile(src) as z:
        entries = sorted((i for i in z.infolist() if not i.is_dir()),
                         key=lambda i: i.file_size, reverse=True)
    buckets, loads = [[] for _ in range(n)], [0] * n
    for e in entries:                      # largest first, into the lightest bucket
        k = loads.index(min(loads))
        buckets[k].append(e.filename)
        loads[k] += e.file_size
    with ProcessPoolExecutor(n) as ex:
        list(ex.map(work, buckets))
