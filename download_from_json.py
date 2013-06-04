import os.path
import platform
import os
import subprocess
import sys
import threading
import Queue
import logging
import json


class DownloadThread(threading.Thread):
    def __init__(self, queue, save_dirctory):
        threading.Thread.__init__(self)
        self.queue = queue
        self.save_dirctory = save_dirctory

    def run(self):
        while True:
            url, save_name = self.queue.get()
            file_name = save_name
            save_path = os.path.join(self.save_dirctory, file_name)
            download(url, save_path)
            self.queue.task_done()


def download(url, save_path):
    url = '"' + url + '"'
    cmd = u'wget ' + url + u' -O ' + save_path
    # different operation systems have different encoding format.
    # Windows: 'mbcs'; Linux: 'utf-8'.
    cmd = cmd.encode(sys.getfilesystemencoding())
    try:
        subprocess.call(cmd, shell=True)
    except:
        logging.error('can not download: %s' % url)
    return None


def download_all(json_path, save_dirctory):
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'log-hhr.txt'),
                        level=logging.DEBUG, filemode='w',
                        format='%(asctime)s - %(levelname)s: %(message)s')
    if not os.path.exists(save_dirctory):
        os.makedirs(save_dirctory)
    # multi-threading fetch all the video urls.
    queue = Queue.Queue()
    json_obj = json.load(open(json_path, 'rb'))
    for item in json_obj:
        queue.put((item['download_url'], item['save_name']))
    for i in range(5):
        dt = DownloadThread(queue, save_dirctory)
        dt.setDaemon(True)
        dt.start()
    queue.join()
    print 'Done!'
    print 'saved in: ' + save_dirctory
    print 'log file: ' + os.path.join(os.getcwd(), 'log-hhr.txt')
    return None


def main():
    json_path = ['gcw.json', 'fashion.json', 'fitness.json', 'meishi.json']
    save_dirctory = ['/data/glustervtc/f4vvideo/tangdou/%s/20130604' % j.split('.')[0] for j in json_path]
    for i in range(len(json_path)):
        download_all(json_path[i], save_dirctory[i])
    return None

if __name__ == '__main__':
    main()
