"""Получение характеристик Pokémon из PokéAPI и построение пяти диаграмм."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_URL = "https://pokeapi.co/api/v2/"
HERE = Path(__file__).resolve().parent


def read_resource(session, url, cache, offline=False, refresh=False):
    """Прочитать JSON из кэша или API; таймаут ограничивает ожидание сети."""
    import hashlib
    path = cache / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists() and (offline or not refresh):
        return json.loads(path.read_text(encoding='utf-8'))
    if offline:
        raise FileNotFoundError(f'Нет кэша для {url}. Выполните запуск с сетью.')
    response = session.get(url, timeout=(5, 20))
    response.raise_for_status()
    data = response.json()
    cache.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    temp.replace(path)
    return data


def parse_pokemon(raw):
    """Извлечь обязательные характеристики и дополнительно скорость и типы.

    height и weight сохраняются в исходных единицах API: дм и гектограммах.
    """
    stats = {item['stat']['name']: item['base_stat'] for item in raw['stats']}
    return {'id': raw['id'], 'name': raw['name'], 'height': raw['height'],
            'weight': raw['weight'], 'hp': stats['hp'], 'attack': stats['attack'],
            'defense': stats['defense'], 'speed': stats['speed'],
            'types': [item['type']['name'] for item in raw['types']]}


def collect(limit, cache, offline=False, refresh=False):
    """Получить список Pokémon, затем характеристики по адресу каждого."""
    if not 1 <= limit <= 100:
        raise ValueError('Количество должно быть от 1 до 100.')
    data = []
    with requests.Session() as session:
        listing = read_resource(session, f'{BASE_URL}pokemon?limit={limit}', cache, offline, refresh)
        for item in listing['results']:
            if not item['url'].startswith(BASE_URL + 'pokemon/'):
                raise ValueError('Неожиданный адрес ресурса API.')
            data.append(parse_pokemon(read_resource(session, item['url'], cache, offline, refresh)))
    if not data:
        raise ValueError('API вернул пустой список.')
    return data


def plot_data(data, output):
    """Сохранить пять разных типов графиков с подписями и аннотациями."""
    if not data:
        raise ValueError('Нельзя построить графики для пустой выборки.')
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    names = [p['name'] for p in data]
    def save(fig, filename):
        fig.tight_layout()
        fig.savefig(output / filename, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 5))
    for key, label in [('hp', 'Здоровье'), ('attack', 'Атака'), ('defense', 'Защита')]:
        ax.plot(names, [p[key] for p in data], marker='o', label=label)
    ax.set(title='Боевые характеристики Pokémon', xlabel='Pokémon', ylabel='Базовые очки')
    ax.tick_params(axis='x', rotation=45); ax.legend(); ax.grid(alpha=.2)
    best = max(data, key=lambda p: p['hp'])
    ax.annotate('Максимум HP', (names.index(best['name']), best['hp']), xytext=(0, 12), textcoords='offset points')
    save(fig, '01_line.png')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter([p['height']/10 for p in data], [p['weight']/10 for p in data], c=[p['speed'] for p in data], cmap='viridis', s=75)
    # Разводим подписи по вертикали: близкие точки остаются читаемыми.
    gap = max(p['weight']/10 for p in data) * .065 or 1
    label_y = -gap
    for p in sorted(data, key=lambda p: p['weight']):
        label_y = max(p['weight']/10, label_y + gap)
        ax.annotate(p['name'], (p['height']/10, p['weight']/10),
                    xytext=(p['height']/10 + .05, label_y), fontsize=8,
                    arrowprops={'arrowstyle':'-', 'color':'#888', 'lw':.6})
    ax.set_ylim(0, label_y + gap * 2)
    ax.set_xlim(0, max(p['height']/10 for p in data) * 1.25)
    fig.colorbar(ax.collections[0], ax=ax, label='Скорость, базовые очки')
    ax.set(title='Рост и масса Pokémon', xlabel='Рост, м', ylabel='Масса, кг');ax.grid(alpha=.2)
    save(fig, '02_scatter.png')
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(names, [p['attack'] for p in data], color='#287f8e'); ax.bar_label(bars, padding=3)
    ax.set(title='Сравнение атаки', xlabel='Pokémon', ylabel='Атака, базовые очки');ax.tick_params(axis='x', rotation=45);ax.margins(y=.15)
    save(fig, '03_bar.png')
    fig, ax = plt.subplots(figsize=(10, 5))
    values = [p['weight']/10 for p in data]
    ax.hist(values, bins=min(6, len(data)), color='#cf7d38', edgecolor='white')
    ax.axvline(sum(values)/len(values), linestyle='--', color='#333', label=f'Среднее {sum(values)/len(values):.1f} кг')
    ax.set(title='Распределение массы', xlabel='Масса, кг', ylabel='Количество Pokémon');ax.legend()
    ax.text(.98,.95,f'n = {len(data)}',transform=ax.transAxes,ha='right',va='top')
    save(fig, '04_hist.png')
    from collections import Counter
    types = Counter(p['types'][0] for p in data)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(types.values(), labels=[f'{k} ({v})' for k,v in types.items()], autopct='%1.1f%%', startangle=90)
    ax.set_title('Доли основных типов Pokémon')
    fig.text(.5,.02,'У каждого Pokémon учитывается только первый тип из API.',ha='center')
    save(fig, '05_pie.png')


def main(argv=None):
    """Запустить сбор и визуализацию, вернуть код завершения."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--offline', action='store_true', help='Использовать только сохранённый кэш')
    parser.add_argument('--refresh', action='store_true', help='Обновить данные из API')
    parser.add_argument('--output', type=Path, default=HERE/'results')
    parser.add_argument('--cache', type=Path, default=HERE/'cache')
    args = parser.parse_args(argv)
    if args.offline and args.refresh:
        parser.error('--offline и --refresh несовместимы')
    try:
        data = collect(args.limit, args.cache, args.offline, args.refresh)
        plot_data(data, args.output)
        result = {'source': BASE_URL, 'generated_at': datetime.now(timezone.utc).isoformat(), 'data': data}
        (args.output/'pokemon.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    except (requests.RequestException, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Ошибка получения или обработки данных: {error}\n')
    print(f'Получено Pokémon: {len(data)}. Данные и 5 графиков: {args.output}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
