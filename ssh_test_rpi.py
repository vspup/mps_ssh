import paramiko
import time
import logging
from tabulate import tabulate
from colorama import Fore, Style

from private import *

INPUT = False

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def get_user_input():
    if INPUT:
        """Запрашивает у пользователя данные для подключения."""
        host = input("Введите IP-адрес Raspberry Pi: ").strip() or "192.168.8.209"
        username = input("Введите имя пользователя (по умолчанию 'pi'): ").strip() or LOGIN
        password = input("Введите пароль: ").strip() or PASSWD
        interval = input("Введите интервал проверки в секундах (по умолчанию 300): ").strip()
        interval = int(interval) if interval.isdigit() else 60

    else:
        host = IP
        username = LOGIN
        password = PASSWD
        interval = DT
    return host, username, password, interval

def check_raspberry_pi(host, username, password):
    """Функция для проверки доступности Raspberry Pi через SSH."""
    try:
        print(f"\n>>>> Подключение к {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)

        # Получаем uptime
        stdin, stdout, stderr = ssh.exec_command('uptime')
        uptime = stdout.read().decode().strip()

        # Получаем состояние памяти
        stdin, stdout, stderr = ssh.exec_command('free -h')
        memory_status = stdout.read().decode().strip().split("\n")

        # Получаем загрузку процессора
        stdin, stdout, stderr = ssh.exec_command('top -bn1 | grep "Cpu(s)"')
        cpu_usage = stdout.read().decode().strip()

        # Выполняем команду для получения процессов
        command = "ps aux --sort=-%mem | head -n 9"
        stdin, stdout, stderr = ssh.exec_command(command)
        processes = stdout.read().decode().strip().split("\n")

        ssh.close()

        # Форматируем данные в таблицу
        table_data = []

        # Добавляем uptime
        table_data.append([Fore.CYAN + "Uptime" + Style.RESET_ALL, uptime])

        # Добавляем память
        mem_header = memory_status[0].split()
        mem_values = memory_status[1].split()
        #table_data.append([Fore.GREEN + "Memory Total" + Style.RESET_ALL, mem_values[1]])
        table_data.append([Fore.YELLOW + "Memory Used" + Fore.CYAN, mem_values[2]])
        #table_data.append([Fore.BLUE + "Memory Free" + Style.RESET_ALL, mem_values[3]])

        # Добавляем swap
        swap_values = memory_status[2].split()
        #table_data.append([Fore.MAGENTA + "Swap Total" + Style.RESET_ALL, swap_values[1]])
        #table_data.append([Fore.RED + "Swap Free" + Style.RESET_ALL, swap_values[2]])

        # Добавляем CPU
        table_data.append([Fore.CYAN + "CPU Usage" + Style.RESET_ALL, cpu_usage])

        # Печатаем таблицу
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="pretty"))

        # Парсим вывод команды
        headers = processes[0].split()[:6] + ["COMMAND"]
        table_data = []
        for process in processes[1:]:
            # Разбиваем строку на части, ограничиваясь первыми 10 столбцами
            parts = process.split(maxsplit=10)
            if len(parts) > 10:
                table_data.append(parts[:6] + [parts[10]])

        # Печатаем таблицу
        print(tabulate(table_data, headers=headers, tablefmt="pretty"))


    except Exception as e:
        logger.error(f"Ошибка подключения: {e}")



if __name__ == "__main__":
    logger.info("Запуск программы для проверки Raspberry Pi.")
    
    # Получение данных от пользователя
    host, username, password, interval = get_user_input()

    while True:
        check_raspberry_pi(host, username, password)
        time.sleep(interval)
