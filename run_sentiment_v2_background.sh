#!/bin/bash
# Скрипт для запуска нового sentiment анализа в фоне

cd ~/Desktop/Haskel/bsp2

echo "Запуск нового sentiment анализа (v2) в фоне..."
nohup python3 bsp2/test_batch_sentiment.py > sentiment_v2.log 2>&1 &
echo $! > sentiment_v2.pid

echo "✅ test_batch_sentiment.py запущен в фоне"
echo "   Логи: sentiment_v2.log"
echo "   PID: $(cat sentiment_v2.pid)"
echo ""
echo "Для проверки прогресса:"
echo "   tail -f sentiment_v2.log"
echo ""
echo "Для остановки:"
echo "   kill $(cat sentiment_v2.pid)"

