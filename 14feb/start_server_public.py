#!/usr/bin/env python3
"""
HTTP сервер с публичным доступом через ngrok
Требуется установленный ngrok: https://ngrok.com/download
"""
import http.server
import socketserver
import os
import webbrowser
import subprocess
import time
import socket

PORT = 8000

# Переходим в директорию скрипта
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

# Слушаем на всех интерфейсах
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print("=" * 60)
    print("🚀 Локальный сервер запущен!")
    print(f"📱 Локальный доступ: http://localhost:{PORT}")
    print("=" * 60)
    
    # Проверяем, установлен ли ngrok
    try:
        result = subprocess.run(['which', 'ngrok'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🌐 Запускаю ngrok для публичного доступа...")
            print("=" * 60)
            
            # Запускаем ngrok в фоне
            ngrok_process = subprocess.Popen(
                ['ngrok', 'http', str(PORT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Ждем немного, чтобы ngrok запустился
            time.sleep(3)
            
            # Получаем публичный URL из ngrok API
            try:
                import urllib.request
                import json
                response = urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels')
                data = json.loads(response.read().decode())
                public_url = data['tunnels'][0]['public_url']
                
                print("✅ Публичный доступ создан!")
                print(f"🌍 Публичная ссылка: {public_url}")
                print("=" * 60)
                print("📋 Отправьте эту ссылку другу - она работает из любой точки мира!")
                print("=" * 60)
                print("💡 Нажмите Ctrl+C чтобы остановить сервер и ngrok")
                print("=" * 60)
                
                # Автоматически открываем браузер
                try:
                    webbrowser.open(public_url)
                except:
                    pass
                    
            except Exception as e:
                print("⚠️  Не удалось получить публичный URL автоматически")
                print("   Откройте http://127.0.0.1:4040 в браузере, чтобы увидеть ссылку")
                print(f"   Ошибка: {e}")
        else:
            print("⚠️  ngrok не установлен!")
            print("=" * 60)
            print("📥 Установите ngrok:")
            print("   1. Скачайте: https://ngrok.com/download")
            print("   2. Распакуйте и добавьте в PATH")
            print("   3. Или используйте: brew install ngrok/ngrok/ngrok")
            print("=" * 60)
            print("💡 Альтернатива: используйте start_server_netlify.py")
            print("=" * 60)
            
    except Exception as e:
        print(f"⚠️  Ошибка при проверке ngrok: {e}")
        print("   Запускаю только локальный сервер...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Останавливаю сервер...")
        try:
            ngrok_process.terminate()
        except:
            pass
        print("✅ Сервер остановлен")
