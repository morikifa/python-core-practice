"""
Задача 5: Шаблон быстрого потокового ввода-вывода (Fast I/O) для контестов.
"""

import sys

def solve() -> None:
    """
    Шаблон для обработки больших объемов данных (до 10^6 чисел) без Time Limit Exceeded.
    """
    # 1. Читаем ВЕСЬ поток ввода сразу и разбиваем по пробелам/переводам строк
    raw_tokens = sys.stdin.read().split()
    if not raw_tokens:
        return

    # 2. Быстрое чтение параметров
    iterator = iter(raw_tokens)
    
    # Пример: первое число N, далее N элементов
    n = int(next(iterator))
    numbers = [int(next(iterator)) for _ in range(n)]

    # 3. Решение алгоритмической задачи (например, подсчет положительных четных чисел)
    answer = sum(1 for x in numbers if x > 0 and x % 2 == 0)

    # 4. Скоростной вывод через sys.stdout.write
    sys.stdout.write(f"{answer}\n")


if __name__ == "__main__":
    solve()
