import invoke
from datetime import datetime


@invoke.task
def crawl(c):
    data_dir = "rawdata/eats"
    now = datetime.now()
    data_file = now.strftime('%y%m%d_%H%M%S') + "_musashinakahara.csv"
    # data_file = now.strftime('%y%m%d_%H%M%S') + "_musashikosugi_search.csv"
    data_path = data_dir + "/" + data_file

    command = "cd ubereats && scrapy crawl shop -o ../" + data_path  # noqa
    invoke.run(command)


@invoke.task
def post(c):
    command = "cd ubereats && rm ../rawdata/eats/shop.csv && scrapy crawl shop -o ../rawdata/shop.csv"  # noqa
    invoke.run(command)


@invoke.task
def trip(c):
    data_dir = "rawdata/trips"
    now = datetime.now()
    data_file = now.strftime('%y%m%d_%H%M%S') + "_trips.csv"
    data_path = data_dir + "/" + data_file

    command = "cd ubereats && scrapy crawl trip -o ../" + data_path  # noqa
    invoke.run(command)
