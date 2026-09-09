"""
Задача 4: Метод скользящего окна (Sliding Window).
Сложность: O(n) по времени, O(1) по памяти.
"""

def max_subarray_sum(numbers: list[int], k: int) -> int | None:
    """
    Находит максимальную сумму непрерывного подмассива длины k.
    
    Объяснение:
    - Вместо вычисления суммы каждого подмассива за O(k * n), мы считаем сумму первых k элементов.
    - Затем сдвигаем окно вправо на 1 позицию: вычитаем ушедший левый элемент и прибавляем новый правый.
    - Время снижается с O(k * n) до O(n).
    """
    if len(numbers) < k or k <= 0:
        return None

    # Сумма первого окна длины k
    current_sum = sum(numbers[:k])
    max_sum = current_sum

    # Сдвиг окна от k до конца массива
    for i in range(k, len(numbers)):
        current_sum += numbers[i] - numbers[i - k]
        if current_sum > max_sum:
            max_sum = current_sum

    return max_sum


if __name__ == "__main__":
    arr = [2, 1, 5, 1, 3, 2]
    k_len = 3
    # Подмассивы длины 3: [2,1,5]=8, [1,5,1]=7, [5,1,3]=9, [1,3,2]=6 -> Max: 9 ([5,1,3])
    print("Максимальная сумма окна k=3:", max_subarray_sum(arr, k_len))  # 9
