"""Первый этап ЛР7. Запускается отдельно от Django, не меняет его логгеры."""
import logging
from pathlib import Path


def main():
    folder=Path(__file__).resolve().parent/'logs'
    folder.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,filename=folder/'basic.log',encoding='utf-8',format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Демонстрация базового логирования')
    logging.warning('Демонстрация предупреждения')
    print(folder/'basic.log')

if __name__=='__main__':
    main()
