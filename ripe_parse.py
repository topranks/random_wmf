#!/usr/bin/python3

import json
import sys
import time

def main():

    json_file = open('RIPE-Atlas-measurement-1790947.json', 'r')
    data = json.load(json_file)
    json_file.close()


    script_time = int(time.time())

    today = {}
    before_today = {}

    for measurement in data:
        if 'x' in measurement['result'][0]:
            if measurement['timestamp'] > (script_time - 86400):
                if measurement['src_addr'] not in today:
                    today[measurement['src_addr']] = 1
                else:
                    today[measurement['src_addr']] += 1
            else:
                if measurement['src_addr'] not in before_today:
                    before_today[measurement['src_addr']] = 1
                else:
                    before_today[measurement['src_addr']] += 1


    for ip, count in today.items():
        print(f"{ip}: {count}")
        


if __name__=="__main__":
    main()

