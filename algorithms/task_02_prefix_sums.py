"""
Задача 2: Префиксные суммы (Prefix Sums).
Сложность: O(n) предобработка, O(1) ответ на каждый запрос.
"""

class PrefixSumArray:
    """
    Класс для быстрого вычисления суммы элементов на отрезке [left, right] включительно.
    """
    def __init__(self, numbers: list[int]) -> None:
        # prefix_sums[i] хранит сумму первых i элементов массива
        self.prefix_sums: list[int] = [0] * (len(numbers) + 1)
        for i, num in enumerate(numbers):
            self.prefix_sums[i + 1] = self.prefix_sums[i] + num

    def query(self, left: int, right: int) -> int:
        """
        Возвращает сумму элементов от индекса left до right включительно за O(1).
        Формула: prefix_sums[right + 1] - prefix_sums[left]
        """
        if left < 0 or right >= len(self.prefix_sums) - 1 or left > right:
            raise IndexError("Некорректный диапазон индексов.")
        return self.prefix_sums[right + 1] - self.prefix_sums[left]


if __name__ == "__main__":
    data = [2, 4, 1, 7, 5, 3]
    psa = PrefixSumArray(data)
    # Сумма с 1 по 3 индекс (4 + 1 + 7 = 12)
    print("Сумма отрезка [1, 3]:", psa.query(1, 3))
    # Сумма всего массива (2 + 4 + 1 + 7 + 5 + 3 = 22)
    print("Сумма всего массива [0, 5]:", psa.query(0, 5))
