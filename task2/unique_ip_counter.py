import time
import random
import mmh3
import pandas as pd
from collections import defaultdict

class HyperLogLog:
    def __init__(self, precision: int = 10):
        """
        Инициализация HyperLogLog.

        :param precision: Количество бит для регистров (влияет на точность).
        """
        self.p = precision
        self.m = 2 ** self.p  # Количество регистров
        self.registers = [0] * self.m

    def add(self, item: str):
        """
        Добавляет IP-адрес в структуру HyperLogLog.

        :param item: IP-адрес.
        """
        hash_value = mmh3.hash(item, signed=False)
        register_index = hash_value & (self.m - 1)  # Определение регистра
        leading_zeros = self._count_leading_zeros(hash_value >> self.p) + 1
        self.registers[register_index] = max(self.registers[register_index], leading_zeros)

    def count(self) -> int:
        """
        Подсчитывает приблизительное количество уникальных IP-адресов.

        :return: Оценка количества уникальных элементов.
        """
        alpha_m = 0.7213 / (1 + 1.079 / self.m)
        Z = sum(2.0 ** -r for r in self.registers)
        estimate = alpha_m * (self.m ** 2) / Z

        return int(estimate)

    @staticmethod
    def _count_leading_zeros(x: int) -> int:
        """Подсчет количества ведущих нулей в бинарном представлении."""
        return len(bin(x)) - len(bin(x).lstrip('0b1'))


def exact_count(ip_list):
    """
    Точный подсчет уникальных IP-адресов с помощью множества (set).

    :param ip_list: Список IP-адресов.
    :return: Количество уникальных элементов.
    """
    return len(set(ip_list))


if __name__ == "__main__":
    # Генерация случайного списка IP-адресов
    num_ips = 100_000
    ips = [f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(num_ips)]

    # Точный подсчет
    start = time.time()
    exact_result = exact_count(ips)
    exact_time = time.time() - start

    # Подсчет с помощью HyperLogLog
    hll = HyperLogLog(precision=10)
    start = time.time()
    for ip in ips:
        hll.add(ip)
    hll_result = hll.count()
    hll_time = time.time() - start

    # Вывод результатов в виде таблицы
    df = pd.DataFrame({
        "Метод": ["Точный подсчет", "HyperLogLog"],
        "Уникальные элементы": [exact_result, hll_result],
        "Время выполнения (сек.)": [exact_time, hll_time]
    })

    # Вывод в консоль вместо ace_tools
    print("\nРезультаты сравнения:\n")
    print(df)
