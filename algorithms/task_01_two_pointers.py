"""
Задача 1: Метод двух указателей (Two Pointers).
Сложность: O(n) по времени, O(1) по памяти.
"""

def find_pair_with_sum(numbers: list[int], target: int) -> tuple[int, int] | None:
    """
    Находит два числа в отсортированном массиве, дающих в сумме target.
    
    Объяснение:
    - Левый указатель (left) указывает на наименьший элемент (индекс 0).
    - Правый указатель (right) указывает на наибольший элемент (индекс len - 1).
    - Если сумма текущих элементов меньше target -> увеличиваем левый индекс (сдвигаем к большим числам).
    - Если сумма больше target -> уменьшаем правый индекс (сдвигаем к меньшим числам).
    - Если равна -> возвращаем пару.
    """
    left = 0
    right = len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]
        if current_sum == target:
            return (numbers[left], numbers[right])
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return None


if __name__ == "__main__":
    test_arr = [1, 3, 5, 7, 10, 14, 19]
    print("Результат для target=17:", find_pair_with_sum(test_arr, 17))  # (7, 10)
    print("Результат для target=100:", find_pair_with_sum(test_arr, 100))  # None
