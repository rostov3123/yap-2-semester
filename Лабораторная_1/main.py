"""Лабораторная 1. Получение данных PokeAPI и визуализация."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

import matplotlib.pyplot as plt
import requests


BASE_URL = "https://pokeapi.co/api/v2/"
LIMIT = 10
OUT_DIR = Path("charts")


FALLBACK = [
    {"id": 1, "name": "bulbasaur", "height": 7, "weight": 69, "hp": 45, "attack": 49, "defense": 49, "speed": 45},
    {"id": 2, "name": "ivysaur", "height": 10, "weight": 130, "hp": 60, "attack": 62, "defense": 63, "speed": 60},
    {"id": 3, "name": "venusaur", "height": 20, "weight": 1000, "hp": 80, "attack": 82, "defense": 83, "speed": 80},
    {"id": 4, "name": "charmander", "height": 6, "weight": 85, "hp": 39, "attack": 52, "defense": 43, "speed": 65},
    {"id": 5, "name": "charmeleon", "height": 11, "weight": 190, "hp": 58, "attack": 64, "defense": 58, "speed": 80},
    {"id": 6, "name": "charizard", "height": 17, "weight": 905, "hp": 78, "attack": 84, "defense": 78, "speed": 100},
    {"id": 7, "name": "squirtle", "height": 5, "weight": 90, "hp": 44, "attack": 48, "defense": 65, "speed": 43},
    {"id": 8, "name": "wartortle", "height": 10, "weight": 225, "hp": 59, "attack": 63, "defense": 80, "speed": 58},
    {"id": 9, "name": "blastoise", "height": 16, "weight": 855, "hp": 79, "attack": 83, "defense": 100, "speed": 78},
    {"id": 10, "name": "caterpie", "height": 3, "weight": 29, "hp": 45, "attack": 30, "defense": 35, "speed": 45},
]


@dataclass
class Pokemon:
    id: int
    name: str
    height: int
    weight: int
    hp: int
    attack: int
    defense: int
    speed: int


def stat(stats, name):
    return next(item["base_stat"] for item in stats if item["stat"]["name"] == name)


def load_pokemon(limit=LIMIT):
    """Возвращает список словарей с характеристиками покемонов."""
    try:
        response = requests.get(f"{BASE_URL}pokemon?limit={limit}", timeout=10)
        response.raise_for_status()
        result = []
        for item in response.json()["results"]:
            details = requests.get(item["url"], timeout=10)
            details.raise_for_status()
            raw = details.json()
            pokemon = Pokemon(
                id=raw["id"],
                name=raw["name"],
                height=raw["height"],
                weight=raw["weight"],
                hp=stat(raw["stats"], "hp"),
                attack=stat(raw["stats"], "attack"),
                defense=stat(raw["stats"], "defense"),
                speed=stat(raw["stats"], "speed"),
            )
            result.append(asdict(pokemon))
        return result
    except requests.RequestException as exc:
        print(f"API недоступен, использую локальный набор данных: {exc}")
        return FALLBACK[:limit]


def save_json(data):
    Path("pokemon.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def annotate_bars(values):
    for i, value in enumerate(values):
        plt.text(i, value + max(values) * 0.02, str(value), ha="center", fontsize=8)


def build_charts(data):
    OUT_DIR.mkdir(exist_ok=True)
    names = [item["name"] for item in data]
    hp = [item["hp"] for item in data]
    attack = [item["attack"] for item in data]
    defense = [item["defense"] for item in data]
    speed = [item["speed"] for item in data]
    weight = [item["weight"] for item in data]
    height = [item["height"] for item in data]

    plt.figure(figsize=(10, 5))
    plt.plot(names, hp, marker="o", label="HP")
    plt.plot(names, attack, marker="s", label="Attack")
    plt.xticks(rotation=35, ha="right")
    plt.title("HP и атака покемонов")
    plt.ylabel("Очки")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "01_line_hp_attack.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(weight, height, s=[s * 4 for s in speed], c=attack, cmap="viridis")
    for item in data:
        plt.annotate(item["name"], (item["weight"], item["height"]), fontsize=8)
    plt.title("Связь веса и роста")
    plt.xlabel("Вес")
    plt.ylabel("Рост")
    plt.colorbar(label="Attack")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "02_scatter_weight_height.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.bar(names, defense, color="#4f8fc0")
    annotate_bars(defense)
    plt.xticks(rotation=35, ha="right")
    plt.title("Защита покемонов")
    plt.ylabel("Defense")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "03_bar_defense.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.barh(names, speed, color="#67a96b")
    plt.title("Скорость покемонов")
    plt.xlabel("Speed")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "04_barh_speed.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(weight, bins=6, color="#b46a6a", edgecolor="black")
    plt.title("Распределение веса")
    plt.xlabel("Вес")
    plt.ylabel("Количество")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "05_hist_weight.png")
    plt.close()

    plt.figure(figsize=(7, 7))
    plt.pie(attack, labels=names, autopct="%1.1f%%", startangle=90)
    plt.title("Доля атаки по покемонам")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "06_pie_attack.png")
    plt.close()


def main():
    data = load_pokemon()
    save_json(data)
    build_charts(data)
    print(f"Получено {len(data)} записей. JSON и графики сохранены.")


if __name__ == "__main__":
    main()
