#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gzip
import re
import fnmatch
import json
import datetime
import argparse
import numpy
import logging
import sys
from string import Template


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

log = logging.getLogger(__name__)
rx_date = re.compile(r"log\-(\d{4})(\d{2})(\d{2}).", re.MULTILINE)
rx_log_line = re.compile(
    r"\S+\s+(\S+|-)\s+(-|\S+)\s\[(?P<date>.+)\]\s+\"((GET|POST|HEAD|PUT|OPTIONS)\s+(?P<url>.*)"
    '\s+HTTP/\d+.\d+|0)"\s+\d+\s+\d+\s+(?P<other>.*)',
    re.MULTILINE,
)
LOCAL_CONFIG = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


def check_config(config):
    if config.get("LOG_DIR") and not os.path.isdir(config["LOG_DIR"]):
        raise Exception("Not LOG_DIR or bad path")
    elif config.get("LOGGING_DIR") and not os.path.isdir(config["LOGGING_DIR"]):
        raise Exception("Not LOGGING_DIR or bad path")
    elif config.get("REPORT_DIR") and not os.path.isdir(config["REPORT_DIR"]):
        raise Exception("Not REPORT_DIR or bad path")
    elif config.get("REPORT_SIZE") and not isinstance(config["REPORT_SIZE"], int):
        raise Exception("REPORT_SIZE is not integer")
    else:
        return config


def get_date(filename):
    date = []
    for name in filename:
        matched = rx_date.search(name)
        if matched:
            y, m, d = map(int, matched.groups())
            if datetime.date(y, m, d):
                date.append(datetime.date(y, m, d))
        else:
            log.exception("No log file in log dir")
            raise Exception
    return max(date)


def check_report(last_date, report_dir):
    for path, dirlist, filelist in os.walk(report_dir):
        for name in fnmatch.filter(filelist, "report-*.html"):
            if last_date in name:
                return True


def gen_find(filepat, log_dir, report_dir):
    data = []
    for path, dirlist, filelist in os.walk(log_dir):
        if not filelist:
            raise StopIteration("No logfiles in log dir %s" % log_dir)
        log.info("View file in log dir %s" % log_dir)
        for name in fnmatch.filter(filelist, filepat):
            data.append(name.encode("utf8"))
    last_date = get_date(data)
    if last_date:
        if check_report(last_date.strftime("%Y.%m.%d"), report_dir):
            raise StopIteration("Report Already created")
        filename = [fn for fn in data if last_date.strftime("%Y%m%d") in fn]
        logging.info("Path: %s, filename: %s", path, filename[0])
        return [os.path.join(path, filename[0]), last_date.strftime("%Y.%m.%d")]


def gen_open(filename):
    if filename.endswith(".gz"):
        yield gzip.open(filename)
    else:
        yield open(filename)


def gen_cat(sources):
    for s in sources:
        for item in s:
            yield item


def median(l):
    return numpy.median(numpy.array(l))


def log_parser(lines, config):
    result = {}
    logs = []
    request_time_sum = 0
    r_size, c_line, s_line = 0, 0, 0
    for line in lines:
        c_line = c_line + 1
        if rx_log_line.search(line):
            s_line = s_line + 1
            for r in rx_log_line.finditer(line):
                url, request_time = r.group("url"), r.group("other").split()[-1]
                request_time_sum = float(request_time_sum) + float(request_time)
                if result:
                    if result.get(url):
                        result[url]["request_time"].append(float(request_time))
                        result[url]["count"] = result[url]["count"] + 1
                        result[url]["time_sum"] = result[url]["time_sum"] + float(
                            request_time
                        )
                    else:
                        result[url] = {
                            "request_time": [float(request_time)],
                            "count": 1,
                            "time_sum": float(request_time),
                        }
                else:
                    result[url] = {
                        "request_time": [float(request_time)],
                        "count": 1,
                        "time_sum": float(request_time),
                    }
    if c_line > s_line:
        raise Exception("Parsed line %s <  %s all lines" % (s_line, c_line))
    counts = sorted(
        set([round(c["time_sum"], 2) for c in result.values()]), reverse=True
    )
    l_counts = (
        counts[0:config["REPORT_SIZE"]]
        if config["REPORT_SIZE"] < len(counts)
        else counts
    )
    for k, v in result.items():
        if r_size == config["REPORT_SIZE"]:
            return logs
        if round(v["time_sum"], 2) not in l_counts:
            continue
        logs.append(
            {
                "url": k,
                "count": v["count"],
                "count_perc": round((100.00 / float(c_line)) * v["count"], 3),
                "time_sum": round(v["time_sum"], 3),
                "time_perc": round(
                    (100.00 / float(request_time_sum)) * v["time_sum"], 3
                ),
                "time_avg": round(v["time_sum"] / float(v["count"]), 3),
                "time_max": max(v["request_time"]),
                "time_med": round(median(v["request_time"]), 3),
            }
        )
        r_size = r_size + 1
    return logs


def main(config):
    if config.get("LOGGING_DIR"):
        out_hdlr = logging.StreamHandler(
            logging.basicConfig(
                format="[%(asctime)s] %(levelname).1s %(message)s",
                datefmt="%Y.%m.%d %H:%M:%S",
                filename=os.path.join(
                    config["LOGGING_DIR"], "log_%s.log" % datetime.date.today()
                ),
            )
        )
        out_hdlr.setLevel(logging.INFO)
        log.addHandler(out_hdlr)
        log.setLevel(logging.INFO)
    else:
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname).1s %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
            )
        )
        out_hdlr.setLevel(logging.INFO)
        log.addHandler(out_hdlr)
        log.setLevel(logging.INFO)
    log.info("Start log parser")
    filename, date = gen_find(
        "nginx-access-ui.log-*", config["LOG_DIR"], config["REPORT_DIR"]
    )
    logfiles = gen_open(filename)
    loglines = gen_cat(logfiles)
    result = log_parser(loglines, config)
    if not result:
        result = [
            {
                "url": None,
                "count": None,
                "count_perc": None,
                "time_sum": None,
                "time_perc": None,
                "time_avg": None,
                "time_max": None,
                "time_med": None,
            }
        ]
    try:
        html = open("report.html")
        report = Template(html.read())
        f = open(os.path.join(config["REPORT_DIR"], "report-%s.html" % date), "w+")
        f.write(report.safe_substitute(table_json=json.dumps(result)))
        f.close()
        html.close()
    except Exception as e:
        raise Exception(logging.exception("Error %s" % e))


if __name__ == "__main__":
    conf_file = {}
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="ext_config", action="store", default=None)
    args = parser.parse_args()
    config = check_config(LOCAL_CONFIG)
    if args.ext_config:
        if not os.path.isfile(args.ext_config):
            raise Exception("Bad config file path")
        ext_config = open(args.ext_config, "r")
        try:
            ext_config = json.loads(ext_config.read())
        except Exception as e:
            raise Exception("Bad config format %s")
        ext_config = {k: v for k, v in ext_config.items() if v is not None}
        config.update(ext_config)
    main(config)
