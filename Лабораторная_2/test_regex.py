"""Граничные случаи шести регулярных выражений."""
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('regex_lab',Path(__file__).with_name('main.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('value,expected',[
    ('abcde',True),('A12_b',True),('a'*20,True),('a'*21,False),('abcd',False),
    ('1abcd',False),('abcd_',False),('абвгд',False),('ab cd',False),('abcde\n',False)])
def test_login(value,expected):
    assert m.validate_login(value) is expected


def test_dates():
    text='1.2.26, 29/02/2024, 29/02/2025, 1-12-99, 31.04.2025, 01/02-2026, 001.02.2026'
    assert m.find_dates(text)==['1.2.26','29/02/2024','1-12-99']


def test_parse_log():
    assert m.parse_log('2024-02-10 14:23:01 INFO user=ada action=login ip=192.168.1.15')=={
        'date':'2024-02-10','time':'14:23:01','user':'ada','action':'login','ip':'192.168.1.15'}

@pytest.mark.parametrize('line',[
    '2024-02-30 14:23:01 INFO user=ada action=login ip=192.168.1.15',
    '2024-02-10 25:23:01 INFO user=ada action=login ip=192.168.1.15',
    '2024-02-10 14:23:01 INFO user=ada action=login ip=999.168.1.15','not a log'])
def test_bad_log(line):
    with pytest.raises(ValueError):m.parse_log(line)

@pytest.mark.parametrize('value,expected',[('Abcdef!1',True),('abcdef!1',False),('ABCDEF!1',False),('Abcdefgh',False),('Abcdefg1',False),('Ab!1',False),('Abc def!1',False)])
def test_password(value,expected):
    assert m.validate_password(value) is expected

@pytest.mark.parametrize('value,expected',[('a.b+tag@GMAIL.COM',True),('a@gmail.com.evil.org',False),('a..b@gmail.com',False),('.a@gmail.com',False),('a@gmailXcom',False),('a@yandex.ru',True),('a@edu.ru',True),('a@x.edu.ru',False)])
def test_email(value,expected):
    assert m.validate_email(value,['gmail.com','yandex.ru','edu.ru']) is expected

@pytest.mark.parametrize('value',['8(999)123-45-67','+7 999 123 45 67','79991234567',' 8 (999) 123-45-67 '])
def test_phone(value):
    assert m.normalize_phone(value)=='+79991234567'

@pytest.mark.parametrize('value',['9991234567','+19991234567','8(9991234567','8x9991234567','8 999 123 45 678'])
def test_bad_phone(value):
    with pytest.raises(ValueError):m.normalize_phone(value)


def test_date_before_sentence_period():
    assert m.find_dates('Встреча 1.2.26. Затем 02/03/2026!')==['1.2.26','02/03/2026']
    assert m.find_dates('1.2.2026.123')==[]
