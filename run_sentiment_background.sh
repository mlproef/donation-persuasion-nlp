#!/bin/bash

# Скрипт для запуска test_batch_sentiment.py в фоне

echo "Запуск test_batch_sentiment.py в фоне..."
echo "Логи будут сохранены в sentiment.log"

# Запускаем в фоне с перенаправлением вывода
nohup python3 bsp2/test_batch_sentiment.py > sentiment.log 2>&1 &

# Получаем PID процесса
SENTIMENT_PID=$!

echo "✅ Скрипт запущен в фоне"
echo "   PID: $SENTIMENT_PID"
echo "   Логи: sentiment.log"
echo ""
echo "Для просмотра логов в реальном времени:"
echo "   tail -f sentiment.log"
echo ""
echo "Для остановки скрипта:"
echo "   kill $SENTIMENT_PID"
echo ""
echo "Для проверки статуса:"
echo "   ps aux | grep test_batch_sentiment"

# Сохраняем PID в файл для удобства
echo $SENTIMENT_PID > sentiment.pid
echo ""
echo "PID сохранен в sentiment.pid"

