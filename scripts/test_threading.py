import threading
import time

def work():
    for _ in range(int(1e9)):
        x = 10 ** 4

start = time.time()
threads = []
for _ in range(12):
    thread = threading.Thread(target=work)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end = time.time()

print(end - start)
