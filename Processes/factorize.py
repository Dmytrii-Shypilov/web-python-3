from multiprocessing import Pool, cpu_count
from time import time
import logging

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def factorize(number):
    logger.debug(f"Working with number {number} ")
    final_list = []
    for n in range(1, number+1):
        if number % n == 0:
            final_list.append(n)
    return final_list


if __name__ == "__main__":
    numbers = [128, 255, 99999, 10651060]

    # SINCHRONOUS
    sync_start = time()
    final_list = []

    for number in numbers:
        res = factorize(number)
        final_list.append(res)

    # a,b,c,d = final_list
    logger.debug(f"Sync time: {time() - sync_start}")


    # ASYNCHRONOUS
    async_start = time()
    with Pool(cpu_count()) as pool:
        a, b, c, d = pool.map(factorize, numbers)
    
    logger.debug(f"Async time: {time() - async_start}")

    # test results
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316,
                 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]
