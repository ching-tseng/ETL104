import json
import os
import time

import pandas
import requests
from bs4 import BeautifulSoup as bs4

domain = "https://www.104.com.tw/jobs/search/"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/81.0.4044.138 "
                        "Safari/537.36",
          "Referer": ""
          }
df = pandas.DataFrame()
keyword = input("搜尋關鍵字: ")


def set_search(domain):
    global keyword
    searches = dict()
    searches["ro"] = "0"
    searches["keyword"] = keyword
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
    job_dict = dict()
    job_soup = bs4(job_res, "html.parser")
    print("=======================START=======================")
    job_json = json.loads(job_soup.text)
    company = job_json["data"]["header"]
    condition = job_json["data"]["condition"]
    welfrae = job_json["data"]["welfare"]
    jobDetail = job_json["data"]["jobDetail"]

    job_dict["工作名稱"] = company["jobName"]
    job_dict["發佈日期"] = company["appearDate"]
    job_dict["廠商名稱"] = company["custName"]
    job_dict["應徵網址"] = company["custUrl"]
    job_dict["接受角色"] = [role["description"] for role in condition["acceptRole"]["role"]]
    job_dict["工作經歷"] = condition["workExp"]
    job_dict["教育程度"] = condition["edu"]
    job_dict["主修科系"] = condition["major"]
    job_dict["所需技能"] = condition["skill"]
    job_dict["備註說明"] = condition["other"]
    job_dict["福利制度"] = welfrae["tag"]
    job_dict["職位代稱"] = [category["description"] for category in jobDetail["jobCategory"]]
    job_dict["薪資待遇"] = jobDetail["salary"]
    job_dict["上工日期"] = jobDetail["startWorkingDay"]

    set_DF(job_dict)
    print("========================END========================")
    time.sleep(1)


def set_DF(job_dict):
    global df
    columns = list()
    rows = list()
    for keys in job_dict:
        columns.append(keys)
        rows.append(job_dict[keys])

    job_df = pandas.DataFrame([rows], columns=columns)
    df = df.append(job_df)


def main():
    global domain, header, df
    url = set_search(domain)
    header["Referer"] = url
    web_ss = requests.session()
    res = web_ss.get(url, headers=header)

    if res.status_code == 200:
        soup = bs4(res.text, "html.parser")
        job_list = soup.select("article > div > h2 > a")
        process_JobList(job_list)

    # print(df)
    write_to_file(df)


def write_to_file(df):
    global keyword
    file_path = "./Bank104/"
    try:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
    except Exception as e:
        print(f"新增檔案失敗: {e}")
    finally:
        df.to_csv(f"{file_path}{keyword}.csv", encoding="utf-8-sig")
