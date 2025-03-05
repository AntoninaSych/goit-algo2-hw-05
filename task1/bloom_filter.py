import hashlib
import bitarray

class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        """
        Ініціалізація фільтра Блума.

        :param size: Розмір бітового масиву.
        :param num_hashes: Кількість хеш-функцій.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)

    def _hashes(self, item: str):
        """
        Генерує хеші для заданого рядка.

        :param item: Вхідний рядок.
        :return: Генерує num_hashes індексів для встановлення в бітовому масиві.
        """
        for i in range(self.num_hashes):
            hash_value = int(hashlib.md5((item + str(i)).encode()).hexdigest(), 16)
            yield hash_value % self.size

    def add(self, item: str):
        """
        Додає елемент у фільтр Блума.

        :param item: Рядок, який потрібно додати.
        """
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def contains(self, item: str) -> bool:
        """
        Перевіряє, чи є елемент у фільтрі.

        :param item: Рядок для перевірки.
        :return: True, якщо елемент можливо є у фільтрі, False – якщо точно немає.
        """
        return all(self.bit_array[index] for index in self._hashes(item))
