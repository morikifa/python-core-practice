"""
Задача 3: Подсчёт частот элементов (Frequency Map / Хэш-таблица).
Сложность: O(n) по времени, O(n) по памяти.
"""

from collections import Counter

def are_anagrams(str1: str, str2: str) -> bool:
    """
    Проверяет, являются ли две строки анаграммами (состоят из одинаковых символов одинаковой частоты).
    """
    # Игнорируем регистр и пробелы
    clean1 = str1.replace(" ", "").lower()
    clean2 = str2.replace(" ", "").lower()
    return Counter(clean1) == Counter(clean2)


def find_most_frequent_element(numbers: list[int]) -> int | None:
    """
    Возвращает наиболее часто встречающийся элемент массива.
    """
    if not numbers:
        return None
    counts = Counter(numbers)
    # most_common(1) возвращает список кортежей [(элемент, количество)]
    return counts.most_common(1)[0][0]


if __name__ == "__main__":
    print("Анаграммы 'listen' и 'silent':", are_anagrams("listen", "silent"))  # True
    print("Анаграммы 'apple' и 'pale':", are_anagrams("apple", "pale"))        # False
    print("Частый элемент в [1, 3, 2, 3, 4, 3, 2]:", find_most_frequent_element([1, 3, 2, 3, 4, 3, 2]))  # 3
