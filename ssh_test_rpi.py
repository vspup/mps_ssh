import paramiko
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def get_user_input():
    """Запрашивает у пользователя данные для подключения."""
    host = input("Введите IP-адрес Raspberry Pi: ").strip()
    username = input("Введите имя пользователя (по умолчанию 'pi'): ").strip() or "pi"
    password = input("Введите пароль: ").strip()
    interval = input("Введите интервал проверки в секундах (по умолчанию 300): ").strip()
    interval = int(interval) if interval.isdigit() else 300
    return host, username, password, interval

def check_raspberry_pi(host, username, password):
    """Функция для проверки доступности Raspberry Pi через SSH."""
    try:
        # Создаем SSH-клиент
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключаемся к Raspberry Pi
        ssh.connect(host, username=username, password=password, timeout=10)
        logger.info("Raspberry Pi доступен.")
        
        # Выполняем команду (например, проверяем uptime)
        stdin, stdout, stderr = ssh.exec_command('uptime')
        uptime = stdout.read().decode().strip()
        logger.info(f"Uptime: {uptime}\n")
        
        ssh.close()
    except Exception as e:
        logger.error(f"Ошибка подключения: {e}")

if __name__ == "__main__":
    logger.info("Запуск программы для проверки Raspberry Pi.")
    
    # Получение данных от пользователя
    host, username, password, interval = get_user_input()

    while True:
        check_raspberry_pi(host, username, password)
        time.sleep(interval)
