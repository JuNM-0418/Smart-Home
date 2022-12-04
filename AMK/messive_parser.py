from multiprocessing.dummy import freeze_support
import requests as rq
from bs4 import BeautifulSoup as bs
from multiprocessing import Process, Queue, cpu_count
from time import sleep, time
import sys
import os


class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKRED = '\033[31m'
    OKMAGENTA = '\033[35m'
    OKYELLOW = '\033[33m'
    OKGRAY = '\033[1;30m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def colorize(text, color, is_remain=False):
        result = color + str(text)
        if not is_remain:
            result += Color.ENDC
        return result


headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"}
TARGET = "58.127"  # 이거 내 아이피
ID = "infp"
PAGE_SIZE = 1000


def get_live(i, queue):
    data = rq.get(
        f"https://arca.live/b/{ID}?p={i}", headers=headers)
    if data.status_code == 200:
        soup = bs(
            data.text,
            "html.parser"
        )
        elements = soup.select("a.vrow")
        for element in elements:
            tag = element.select_one("small")
            if tag and TARGET == tag.get_text()[1:-1]:
                text = element.get_text().replace("\n", " ")
                link = f"https://arca.live{element.attrs['href']}"
                imparse = rq.get(link)
                if imparse.status_code == 200:
                    image = bs(imparse.text, "html.parser")
                    imagelink = image.select_one(
                        "div.avatar > img").attrs['src']
                    queue.put({"text": text, "link": link, "image": imagelink})
                else:
                    queue.put({"text": text, "link": link, "image": None})


def get_gallery(i, queue):
    GALTYPE = "/mgallery"
    # GALTYPE = ""
    data = rq.get(
        f"https://gall.dcinside.com{GALTYPE}/board/lists/?id={ID}&page={i}", headers=headers)
    if data.status_code == 200:
        soup = bs(
            data.text,
            "html.parser"
        )
        elements = soup.select("tr.ub-content.us-post")
        for element in elements:
            tag = element.select_one("td.gall_writer")
            if tag and TARGET == tag.attrs['data-ip']:
                num = element.select_one("td.gall_num")
                queue.put({"text": element.get_text().replace("\n", " "), "link":
                           f"https://gall.dcinside.com/{GALTYPE}/board/view/?id={ID}&no={num.get_text()}"})


def multi_executor(func, limit=cpu_count()*2):
    queue = Queue()
    start = time()
    is_first = True
    left = len(str(PAGE_SIZE))
    lim_len = len(str(limit))
    threads = [Process(target=func, args=(i, queue))
               for i in range(PAGE_SIZE)]
    added = []
    print('\033[?25l', end="")
    print("thread starts")
    while len(threads) or len(added):
        if len(added) < limit and len(threads) > 0:
            added.append(threads.pop(0))
            added[-1].start()
            if is_first:
                sleep(1)
                is_first = False
        added = [add for add in added if add.is_alive()]
        kval = PAGE_SIZE-len(threads)-len(added)
        per = kval/PAGE_SIZE
        t = time()-start
        it = kval/t if t > 0 else 0
        rate = len(added)/limit
        busy = Color.OKRED + ("*" if len(added) == limit else " ") + Color.ENDC
        termsize = os.get_terminal_size().columns
        text1 = """ ({:%dd}/{:%dd}: {:5.1f}%%, {:7.1f}it/s)""" % (left, left)
        text2 = """ ({:%dd}/{:%dd}, load rate: {:5.1f}%%) {}""" % (lim_len, lim_len)
        text1 = text1.format(kval, PAGE_SIZE, per*100, it)
        text2 = text2.format(len(added), limit, rate*100, busy)

        bar = termsize - max(len(text1), len(text2)) - 2
        p_bar = bar*kval//PAGE_SIZE
        s_bar = bar*len(added)//PAGE_SIZE
        l_bar = bar - p_bar - s_bar

        ss_bar = int(bar*rate)
        sl_bar = bar - ss_bar

        output = ""
        if rate > 0.75:
            output = Color.OKRED
        elif rate > 0.5:
            output = Color.OKMAGENTA
        elif rate > 0.25:
            output = Color.OKYELLOW
        else:
            output = Color.OKBLUE
        sys.stdout.writelines(
            f"\r\033[F[{Color.OKGREEN}{'━'*p_bar}{output}{'━'*s_bar}{Color.OKGRAY}{'━'*l_bar}{Color.ENDC}]{text1}\n")
        sys.stdout.writelines(
            f"[{output}{'━'*ss_bar}{Color.OKGRAY}{'━'*sl_bar}{Color.ENDC}]{text2}")
    print('\033[?25h', end="")
    # text = f"\rleft threads: {len(threads)}, scanning: {len(added)} [{kval}/{PAGE_SIZE}({per:.1f}%, {it:.1f}it/s),  found.] {'busy' if len(added) == limit else ''}"

    print()
    while not queue.empty():
        value = queue.get()
        print(value)
    end = time()
    print(
        f"end with {Color.colorize(round(end-start, 1), Color.OKRED)}s.({PAGE_SIZE/(end-start):.1f}it/s)")


if __name__ == "__main__":
    freeze_support()
    multi_executor(get_gallery, limit=50)
    # try:
    #     for links in tqdm(list_chunk(thread, 50)):
    #         while not queue.empty():
    #             value = queue.get()
    # print(value)
    # if dic.get(value['image']):
    #     dic[value['image']].append(value)
    #     print('added:', len(dic[value['image']]))
    # else:
    #     dic[value['image']] = [value]
    # for key, value in dic.items():
    #     print(key)
    #     for d in value:
    #         print(f"{d['text']}: {d['link']}")
    # except KeyboardInterrupt:
    #     print("interrupted: KeyboardInterrupt")
    # print(dic)
