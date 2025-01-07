from loguru import logger

logger.remove()

app_logger = logger.bind(name="app")
app_logger.add("logs/app.log", rotation="10 MB", retention="1 week", filter=lambda record: record["extra"].get("name") == "app")

result_logger = logger.bind(name="result")
result_logger.add("logs/result.log", rotation="10 MB", retention="1 week", filter=lambda record: record["extra"].get("name") == "result")

data_logger = logger.bind(name="data")
data_logger.add("logs/data.log", rotation="10 MB", retention="1 week", filter=lambda record: record["extra"].get("name") == "data")


def get_logger():
    return app_logger

def get_result_logger():
    return result_logger

def get_data_logger():
    return data_logger