import os
import time
import pathvalidate
import requests
from bs4 import BeautifulSoup as bs4


def set_search(domain):
    searches = dict()
    searches["ro"] = "0"
    searches["keyword"] = "s"
    searches["order"] = "15"
    searches["asc"] = "0"
    searches["mode"] = "s"
    searches["jobsource"] = "2018indexpoc"
    searches["page"] = "1"

    get = "?"
    for key in searches:
        get += f"{key}={searches[key]}&"

    return domain + get


def process_JobList(job_list):
    if len(job_list) == 0:
        print(f"No Jobs:{job_list} Found")
        return

    i = 0
    for job in job_list:
        i += 1
        print(f"Jobs: {i}/ {len(job_list)}")

        global header
        job_code = job.get("href").split("?")[0].split("/")[-1]
        url = f"https://www.104.com.tw/job/ajax/content/{job_code}"
        header["Referer"] = url
        job_res = requests.get(url, headers=header)
        if job_res.status_code == 200:
            get_JobDetail(job_res.text)
        else:
            print(f"#####Get Job:{url} Failed.#####")


def get_JobDetail(job_res):
    job_soup = bs4(job_res, "html.parser")
    print("=======================START=======================")
    print(job_soup.prettify())
    print("========================END========================")
    time.sleep(1)


domain = "https://www.104.com.tw/jobs/search/"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/81.0.4044.138 "
                        "Safari/537.36",
          "Referer": ""
          }


def main():
    global domain, header
    url = set_search(domain)
    header["Referer"] = url
    web_ss = requests.session()
    res = web_ss.get(url, headers=header)

    if res.status_code == 200:
        soup = bs4(res.text, "html.parser")
        job_list = soup.select("article > div > h2 > a")
        process_JobList(job_list)
