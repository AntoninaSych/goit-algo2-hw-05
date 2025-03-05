import time
import mmh3
import json
import pandas as pd

class HyperLogLog:
    def __init__(self, precision: int = 12):
        self.p = precision
        self.m = 2 ** self.p
        self.registers = [0] * self.m

    def add(self, item: str):
        hash_value = mmh3.hash(item, signed=False)
        register_index = hash_value & (self.m - 1)
        leading_zeros = self._count_leading_zeros(hash_value >> self.p) + 1
        self.registers[register_index] = max(self.registers[register_index], leading_zeros)

    def count(self) -> int:
        alpha_m = 0.7213 / (1 + 1.079 / self.m)
        Z = sum(2.0 ** -r for r in self.registers)
        estimate = alpha_m * (self.m ** 2) / Z
        return int(estimate)

    @staticmethod
    def _count_leading_zeros(x: int) -> int:
        return len(bin(x)) - len(bin(x).lstrip('0b1'))

def load_ip_addresses(file_path):
    ip_addresses = set()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                log_entry = json.loads(line.strip())
                ip = log_entry.get("remote_addr")
                if is_valid_ip(ip):
                    ip_addresses.add(ip)
            except json.JSONDecodeError:
                continue
    return list(ip_addresses)

def is_valid_ip(ip):
    if not isinstance(ip, str):
        return False
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def exact_count(ip_list):
    return len(set(ip_list))

if __name__ == "__main__":
    file_path = "lms-stage-access.log"

    print("\nЗагрузка данных из лог-файла...")
    start = time.time()
    ip_addresses = load_ip_addresses(file_path)
    load_time = time.time() - start
    print(f"Загружено {len(ip_addresses)} уникальных IP за {load_time:.2f} сек.")

    print("\nВыполняется точный подсчет уникальных IP-адресов...")
    start = time.time()
    exact_result = exact_count(ip_addresses)
    exact_time = time.time() - start

    print("\nВыполняется подсчет уникальных IP-адресов с HyperLogLog...")
    hll = HyperLogLog(precision=12)
    start = time.time()
    for ip in ip_addresses:
        hll.add(ip)
    hll_result = hll.count()
    hll_time = time.time() - start

    df = pd.DataFrame({
        "Метод": ["Точный подсчет", "HyperLogLog"],
        "Уникальные элементы": [exact_result, hll_result],
        "Время выполнения (сек.)": [exact_time, hll_time]
    })

    print("\nРезультаты сравнения:\n")
    print(df)
