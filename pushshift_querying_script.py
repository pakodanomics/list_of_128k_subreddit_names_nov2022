'''
The below script is released under 
a https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) 
License. 
SHARE-ALIKE: Under the same license 
ATTRIBUTION: Cite this as your source, but without implying I endorse your work
NON-COMMERCIAL: Self-explanatory 
-- 
No warranties or liability for the same. 



CODE EXPLANATION: 
Each thread: 
1) Makes a GET request to PushShift as appropriate (we iterate 100 posts at a time, UTC-time-wise)
2) Checks that we received a 200. If yes, 3) If no, 4) 
3) Writes to a file 
4) Adds that timestamp to a Queue. This queue is later written to RESTARTS.txt
'''


import requests
import time 
from tqdm import tqdm
import os
import threading 
from queue import Queue

def to_threading(utc, restart_q):
    rq = requests.get("https://api.pushshift.io/reddit/submission/search/?filter=subreddit,created_utc&after={}&limit=100&sort=ascd&sort_type=created_utc".format(utc)) 
    if(rq.status_code != 200): 
        restart_q.put(utc)
        print("FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
    else:
        with open("./{}/{}.json".format(NOW_UTC,utc),'w') as f: 
            f.write(rq.text)
def get_all_queue_result(queue):
    result_list = []
    while not queue.empty():
        result_list.append(queue.get())
    return result_list

TIME_AMOUNT_DAYS = 3 
TIME_AMOUNT_SECONDS = TIME_AMOUNT_DAYS*3600*24 
# TIME_AMOUNT_SECONDS = 200 
NOW_UTC = int(time.time())
os.mkdir(str(NOW_UTC))
START_UTC = int(NOW_UTC - TIME_AMOUNT_SECONDS )
SHIFT_AMOUNT = 6 

# utcs_lst = np.arange(start=START_UTC, stop=NOW_UTC, step=SHIFT_AMOUNT).tolist()
utcs_lst = list(range(START_UTC,NOW_UTC, SHIFT_AMOUNT))
INTERVAL = 1.5
threds = []
restart_q  = Queue()
for utc in tqdm((utcs_lst)):
    t1 = time.perf_counter() 
    thred = threading.Thread(target=to_threading, args=(utc, restart_q)) 
    thred.start()
    threds.append(thred) 
    t2 = time.perf_counter()
    time.sleep(max(0,(INTERVAL-(t2 - t1)))) 
[thred.join() for thred in tqdm(threds)]

restarts = get_all_queue_result(restart_q) 
with open("./{}/RESTARTS.txt".format(NOW_UTC),'w') as f: 
    f.writelines([str(i)+'\n' for i in restarts])