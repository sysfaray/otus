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
from string import Template
from collections import defaultdict
from contextlib import contextmanager

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
rx_date = re.compile(r"log\-(\d{4})(\d{2})(\d{2}).", re.MULTILINE)
rx_log_line = re.compile(
    r"\S+\s+(\S+|-)\s+(-|\S+)\s\[(?P<date>.+)\]\s+\"((GET|POST|HEAD|PUT|OPTIONS)\s+(?P<url>.*)"
    '\s+HTTP/\d+.\d+|0)"\s+\d+\s+\d+\s+(?P<other>.*)',
    re.MULTILINE,
)
LOCAL_CONFIG = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


def setup_loggger(log_dir):
    """
    :param log_dir: ./logs
    Данная функция запускает логирование
    Если log_dir указан, но не такой директории, создаем директорию и формируем имя файла лога
    Если log_dir указан и есть директория, то формируем имя файла лога
    Если log_dir is None, задаем filename=None, для отображения логов на экране.
    """
    filename = None
    if log_dir:
        filename = os.path.join(log_dir, "log_%s.log" % datetime.date.today())
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )


def check_config(config):
    """
    :param config: {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log", "LOGGING_DIR": "./logs"}
    :return: {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log", "LOGGING_DIR": "./logs"}
    Функция проверяет корректность конфигурационного файла.
    Если параметры в конфиге не правильные, то возвращаем ошибку и прекращаем выполнение скрипта.
    """
    if config.get("LOG_DIR") and not os.path.isdir(config["LOG_DIR"]):
        raise Exception("Not LOG_DIR or bad path")
    elif config.get("LOGGING_DIR") and not os.path.isdir(config["LOGGING_DIR"]):
        logging.info("Make log dir %s", config.get("LOGGING_DIR"))
        os.makedirs(config.get("LOGGING_DIR"))
    elif config.get("REPORT_DIR") and not os.path.isdir(config["REPORT_DIR"]):
        logging.info("Make report dir %s", config.get("REPORT_DIR"))
        os.makedirs(config.get("REPORT_DIR"))
    elif config.get("REPORT_SIZE") and not isinstance(config["REPORT_SIZE"], int):
        raise Exception("REPORT_SIZE is not integer")
    else:
        return config


def get_date(filenames):
    """
    :param filenames: ['nginx-access-ui.log-20170630.gz', 'nginx-access-ui.log-20170530.gz]
    :return: 2017-06-30
    Функция ищет файл с последней датой в имени файла.
    """
    date = []
    for name in filenames:
        matched = rx_date.search(name)
        if matched:
            y, m, d = map(int, matched.groups())
            if datetime.date(y, m, d):  # проверяем что это формат даты
                date.append(datetime.date(y, m, d))
        else:
            logging.error("No log file in log dir")
            break
    if date:
        return max(date)


def check_report(last_date, report_dir):
    """
    :param last_date: '2017.06.30'
    :param report_dir: './reports'
    :return: True
    Проверяем, что отчет существует
    """
    for path, dirlist, filelist in os.walk(report_dir):
        for name in fnmatch.filter(filelist, "report-*.html"):
            if last_date in name:
                return True


def gen_find(filepat, log_dir, report_dir):
    """
    :param filepat: 'nginx-access-ui.log-*'
    :param log_dir: './log'
    :param report_dir: './reports'
    :return: ('./log/nginx-access-ui.log-20170630.gz', '2017.06.30') or (None, None)
    """
    data = []
    for path, dirlist, filelist in os.walk(log_dir):
        if not filelist:
            logging.error("No logfiles in log dir %s", log_dir)
            break
        logging.info("View file in log dir %s" % log_dir)
        for name in fnmatch.filter(filelist, filepat):
            data.append(name.encode("utf8"))
    last_date = get_date(data)
    if last_date:
        if check_report(last_date.strftime("%Y.%m.%d"), report_dir):
            logging.info(
                "Report: report-%s.html already in %s created",
                last_date.strftime("%Y.%m.%d"),
                report_dir,
            )
            return None, None
        filename = [fn for fn in data if last_date.strftime("%Y%m%d") in fn]
        logging.info("Path: %s, filename: %s", path, filename[0])
        return [os.path.join(path, filename[0]), last_date.strftime("%Y.%m.%d")]
    else:
        return None, None


def gen_open(filename):
    if filename.endswith(".gz"):
        with gzip.open(filename) as o_file:
            content = o_file.read().splitlines()
    else:
        with open(filename, "r") as o_file:
            content = o_file.read().splitlines()
    return content


def median(l):
    return numpy.median(numpy.array(l))


@contextmanager
def file_open(path):
    try:
        f_obj = open(path, "w")
        yield f_obj
    except OSError:
        logging.exception("Houston we have problems!")
    finally:
        logging.info("Closing file")
        f_obj.close()


def log_parser(lines, config):
    """
    Функция парсит строки лог файла.
    Если строка не проходит проверку по регуляркам, выпадает в лог.
    Если число строк которые не удалось распарсить, превышает 2% функция возвращает None, False,
    в следствии чего работа скрипта останавливается.
    """
    result = defaultdict(dict)
    logs = []
    request_time_sum = 0
    r_size, err_line = 0, 0
    p_l = (len(lines) / 100) * 2
    for line in lines:
        line = line.encode("utf-8")
        if rx_log_line.search(line):
            for r in rx_log_line.finditer(line):
                url, request_time = r.group("url"), r.group("other").split()[-1]
                request_time_sum = float(request_time_sum) + float(request_time)
                if result.get(url):
                    result[url]["request_time"] += [(float(request_time))]
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
            err_line = err_line + 1
            logging.error("Log line not supported %s", line)
    if err_line >= p_l:
        logging.error("Error parsed line %s = value: %s", err_line, p_l)
        return None, False
    logging.info("Count error lines %s", err_line)
    counts = sorted(
        set([round(c["time_sum"], 2) for c in result.values()]), reverse=True
    )
    l_counts = (
        counts[0 : config["REPORT_SIZE"]]
        if config["REPORT_SIZE"] < len(counts)
        else counts
    )
    for k, v in result.items():
        if r_size == config["REPORT_SIZE"]:
            logging.info("Results = report size %s", r_size)
            return logs, True
        if round(v["time_sum"], 2) not in l_counts:
            continue
        logs.append(
            {
                "url": k,
                "count": v["count"],
                "count_perc": round((100.00 / float(len(lines))) * v["count"], 3),
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
    return logs, True


def main(config):
    """
    :param config: {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log", "LOGGING_DIR": "./logs"}
    :return: report file
    """
    logging.info("Starting log parser")
    filename, date = gen_find(
        "nginx-access-ui.log-*", config["LOG_DIR"], config["REPORT_DIR"]
    )
    if filename:
        logfiles = gen_open(filename)
        result, status = log_parser(logfiles, config)
        if status:
            if not result:  # если отчет пустой, возвращаем ничего.
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
            logging.info("Starting writing report file report-%s.html", date)
            try:
                html = open("report.html")
                report = Template(html.read())
                with file_open(
                    os.path.join(config["REPORT_DIR"], "report-%s.html" % date)
                ) as f_report:
                    f_report.write(
                        report.safe_substitute(table_json=json.dumps(result))
                    )
                html.close()
                logging.info("Report file report-%s.html created", date)
            except Exception as e:
                raise Exception(logging.exception("Error %s", e))
        else:
            logging.error("More errors in logfile")

    else:
        logging.error(
            "There is no log file of the required format or the report has already been created"
        )


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
            raise Exception("Bad config format %s", e)
        ext_config = {k: v for k, v in ext_config.items() if v is not None}
        config.update(ext_config)
    setup_loggger(config.get("LOGGING_DIR"))
    main(config)
