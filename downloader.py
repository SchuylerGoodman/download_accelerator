import argparse
import os
import requests
import threading

class Downloader:
        def __init__(self):
            self.t_count=1
            self.url=""
            self.parse_arguments()
            self.downloads_dir = "downloads/"


        def parse_arguments(self):
            parser = argparse.ArgumentParser(prog="Download Accelerator", description="A script that downloads a file with multiple threads")
            parser.add_argument("-n", "--threads", type=int, help="Specify the number of threads to use to download", default=1)
            parser.add_argument("url", type=str, help="Specify the URL location of the download")
            args = parser.parse_args()
            self.t_count = args.threads
            self.url = args.url
            if self.url.endswith('/'):
                self.url += "index.html"


        def download(self):
            headers = {'Accept-Encoding': "identity"}
            h_r = requests.get(self.url, headers = headers)
            print h_r.headers
            if 'content-length' not in h_r.headers:
                return
            length = int(h_r.headers['content-length'])
            if length < self.t_count:
                self.t_count = length
            bytes_per_thread = length / self.t_count
            ranges = self.chunks(list(xrange(0, length)), bytes_per_thread)

            threads = []
            for range in ranges:
#                print range
                d = DownThread(self.url, range)
                threads.append(d)

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            with open(self.downloads_dir + self.url.strip("http\/\/:"), 'wb') as f:
                for t in threads:
                    f.write(t.content)



        def chunks(self, l, n):
            for i in xrange(0, len(l), n):
                yield [i, i + n - 1] if i + n < len(l) else [i, len(l) - 1]

class DownThread(threading.Thread):
    def __init__(self, url, range):
        self.url = url
        self.range = range
        threading.Thread.__init__(self)
        self._content_consumed = False
        self.content = []

    def run(self):
        low = self.range[0]
        high = self.range[1]
        print "Downloading bytes {0} to {1} - {2}".format(low, high, self.url)
        headers = \
            {
                'Accept-Encoding': "identity",
                'Range': "bytes={0}-{1}".format(low, high)
            }
        r = requests.get(self.url, stream=True, headers=headers)
        self.content = r.content


if __name__ == '__main__':
    d = Downloader()
    d.download()
