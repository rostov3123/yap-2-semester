"""Единая точка запуска: python run.py setup|serve|test|api|regex."""
import argparse
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT/'django_project'


def run(*args,cwd=ROOT):
    """Выполнить команду текущим Python, сохранив код ошибки."""
    subprocess.run([sys.executable,*map(str,args)],cwd=cwd,check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['setup','serve','test','api','regex'])
    args=parser.parse_args()
    try:
        if args.command=='setup':
            run('-m','pip','install','-r','requirements-lock.txt')
            run('manage.py','migrate','--noinput',cwd=PROJECT)
            run('manage.py','seed_demo',cwd=PROJECT)
            run('manage.py','check',cwd=PROJECT)
        elif args.command=='serve':
            # --insecure раздаёт только учебную статику при DEBUG=False на localhost.
            run('manage.py','runserver','127.0.0.1:8000','--insecure',cwd=PROJECT)
        elif args.command=='test':
            run('-m','pytest','-q','Лабораторная_1','Лабораторная_2')
            run('-m','pytest','-q',cwd=PROJECT)
            run('manage.py','check',cwd=PROJECT)
            run('manage.py','makemigrations','--check','--dry-run',cwd=PROJECT)
        elif args.command=='api':
            run(ROOT/'Лабораторная_1/main.py','--offline')
        else:
            run(ROOT/'Лабораторная_2/main.py')
    except subprocess.CalledProcessError as error:
        return error.returncode
    except KeyboardInterrupt:
        return 130
    return 0

if __name__=='__main__':
    raise SystemExit(main())
