# Эксперимент: проверка, является ли DP 111 (hidden_state) записываемым.
# Скрипт: читает статус -> пишет 111=False -> читает снова ->
# возвращает 111=True обратно -> читает финальное состояние.
#
# Запуск (нужен tinytuya: pip install tinytuya):
#   python3 gate_wfh_dp111.py <IP> <DEVICE_ID> <LOCAL_KEY>
#
# ВНИМАНИЕ: на время теста интеграция LocalTuya в HA может на минуту
# потерять связь с контроллером (одно локальное подключение) — сама
# переподключится после завершения скрипта.

import sys
import time
import tinytuya

if len(sys.argv) < 4:
    print("Использование: python3 gate_wfh_dp111.py <IP> <DEVICE_ID> <LOCAL_KEY>")
    sys.exit(1)

IP, DEV_ID, LOCAL_KEY = sys.argv[1], sys.argv[2], sys.argv[3]

d = tinytuya.Device(DEV_ID, IP, LOCAL_KEY)
d.set_version(3.5)
d.set_socketTimeout(8)


def show(tag):
    data = d.status()
    if isinstance(data, dict) and data.get("dps"):
        print(f"{tag}: DP111 = {data['dps'].get('111')!r}  (весь статус: {data['dps']})")
    else:
        print(f"{tag}: ошибка чтения: {data}")


print("=== DP 111: проверка записи ===")
show("1. До записи          ")

print("2. Пишем 111 = False ...")
d.set_value(111, False)
time.sleep(1)
show("3. После записи False ")

print("4. Возвращаем 111 = True ...")
d.set_value(111, True)
time.sleep(1)
show("5. После записи True  ")

print("""
Выводы:
- Если в п.3 значение осталось True -> DP 111 read-only, это датчик.
- Если в п.3 стало False -> DP 111 ЗАПИСЫВАЕМЫЙ (переключатель).
  Тогда наблюдайте: изменилось ли что-то в приложении Smart Life
  (новая настройка?) или в поведении ворот (открытие/закрытие,
  автозакрытие, скорость). Если ничего не заметно - скорее всего,
  это скрытый флаг прошивки без влияния на работу.
""")
