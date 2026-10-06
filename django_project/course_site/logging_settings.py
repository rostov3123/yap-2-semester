"""Консоль, ротация по размеру и ежедневная ротация с хранением 7 файлов."""
import logging

class CompleteFormatter(logging.Formatter):
    """Дополнить записи taskName для совместимости Python 3.10–3.12."""
    def format(self, record):
        if not hasattr(record, 'taskName'):
            record.taskName = None
        return super().format(record)


def make_logging(base_dir):
    """Собрать dictConfig; пароль и содержимое форм никогда не логируются."""
    folder = base_dir/'logs'
    folder.mkdir(exist_ok=True)
    # msg/args формируют message; exc_info/stack_info Formatter добавляет при наличии.
    detail = ('{asctime} {levelname}({levelno}) {name} {message} '
              '| {pathname}:{lineno} file={filename} module={module} func={funcName} '
              'created={created} msecs={msecs} relative={relativeCreated} '
              'process={process} processName={processName} thread={thread} '
              'threadName={threadName} taskName={taskName} '
              'msg={msg!r} args={args!r} exc_info={exc_info!r} '
              'exc_text={exc_text!r} stack_info={stack_info!r}')
    return {
        'version': 1, 'disable_existing_loggers': False,
        'formatters': {
            'full': {'()': CompleteFormatter, 'format': detail, 'style': '{'},
            'brief': {'format': '{levelname} {name}: {message}', 'style': '{'},
        },
        'handlers': {
            'console': {'class': 'logging.StreamHandler', 'formatter': 'brief', 'level': 'INFO'},
            'size': {'class': 'logging.handlers.RotatingFileHandler', 'filename': folder/'application.log',
                     'maxBytes': 1024*1024, 'backupCount': 3, 'encoding': 'utf-8', 'formatter': 'full'},
            'daily': {'class': 'logging.handlers.TimedRotatingFileHandler', 'filename': folder/'daily.log',
                      'when': 'midnight', 'interval': 1, 'backupCount': 7, 'encoding': 'utf-8', 'formatter': 'full'},
        },
        'root': {'handlers': ['console', 'size', 'daily'], 'level': 'INFO'},
        'loggers': {'django': {'handlers': ['console', 'size', 'daily'], 'level': 'INFO', 'propagate': False}},
    }
