"""Тесты парсинга, сетевых ошибок и автономного кэша без обращения к сети."""
import importlib.util
from pathlib import Path
from unittest.mock import Mock
import pytest
import requests
spec=importlib.util.spec_from_file_location('api_lab',Path(__file__).with_name('main.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def test_parse_by_stat_name():
    raw={'id':1,'name':'test','height':7,'weight':69,
         'stats':[{'stat':{'name':k},'base_stat':v} for k,v in [('speed',45),('defense',49),('attack',49),('hp',45)]],
         'types':[{'type':{'name':'grass'}}]}
    result=m.parse_pokemon(raw)
    assert result['hp']==45 and result['weight']==69 and result['types']==['grass']


def test_cache_and_offline(tmp_path):
    session=Mock();session.get.return_value.json.return_value={'name':'bulbasaur'}
    url=m.BASE_URL+'pokemon/1/'
    assert m.read_resource(session,url,tmp_path)=={'name':'bulbasaur'}
    session.get.assert_called_once_with(url,timeout=(5,20))
    session.get.reset_mock()
    assert m.read_resource(session,url,tmp_path,offline=True)=={'name':'bulbasaur'}
    session.get.assert_not_called()


def test_missing_cache(tmp_path):
    with pytest.raises(FileNotFoundError):m.read_resource(Mock(),m.BASE_URL+'pokemon/2/',tmp_path,offline=True)


def test_network_error(tmp_path):
    session=Mock();session.get.side_effect=requests.Timeout('timeout')
    with pytest.raises(requests.Timeout):m.read_resource(session,m.BASE_URL+'pokemon/1/',tmp_path)
    assert not list(tmp_path.glob('*.json'))

@pytest.mark.parametrize('limit',[0,-1,101])
def test_bad_limit(limit,tmp_path):
    with pytest.raises(ValueError):m.collect(limit,tmp_path)


def test_empty_plot(tmp_path):
    with pytest.raises(ValueError):m.plot_data([],tmp_path)
