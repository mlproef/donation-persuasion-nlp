#!/usr/bin/env python3
"""
Простой HTTP сервер для запуска сайта
"""
import http.server
import socketserver
import os
import webbrowser
import socket
import subprocess

PORT = 8000

# Переходим в директорию скрипта
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Функция для получения IP-адреса
def get_local_ip():
    """Получает локальный IP-адрес"""
    try:
        # Попробуем подключиться к внешнему адресу (не отправляем данные)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Альтернативный способ для Mac
        try:
            result = subprocess.run(['ipconfig', 'getifaddr', 'en0'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "не определен"

Handler = http.server.SimpleHTTPRequestHandler

# Слушаем на всех интерфейсах (0.0.0.0)
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🚀 Сервер запущен!")
    print("=" * 60)
    print(f"📱 Локальный доступ: http://localhost:{PORT}")
    print(f"🌐 Доступ с других устройств: http://{local_ip}:{PORT}")
    print("=" * 60)
    print("📋 Инструкция для друга:")
    print(f"   1. Убедитесь, что вы в одной Wi-Fi сети")
    print(f"   2. Откройте в браузере: http://{local_ip}:{PORT}")
    print("=" * 60)
    print("⚠️  Если не работает:")
    print("   - Проверьте, что оба устройства в одной сети Wi-Fi")
    print("   - Отключите файрвол или разрешите порт 8000")
    print("   - Попробуйте другой порт (измените PORT в скрипте)")
    print("=" * 60)
    print("💡 Нажмите Ctrl+C чтобы остановить сервер")
    print("=" * 60)
    
    # Автоматически открываем браузер
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
