# Тест подключения к контроллеру ворот WFH
# Перебирает версии протокола Tuya и показывает, на какой устройство отвечает.
#
# Запуск (из Terminal & SSH на HA или любого ПК в той же сети):
#   pip install tinytuya
#   python3 test_gate.py <IP> <DEVICE_ID> <LOCAL_KEY>
# Пример: python3 test_gate.py 192.168.1.50 bf0xxxxxxxxxxxxxxxxx "abcd1234!?"

import sys
import tinytuya

if len(sys.argv) < 4:
    print("Использование: python3 test_gate.py <IP> <DEVICE_ID> <LOCAL_KEY>")
    sys.exit(1)

IP, DEV_ID, LOCAL_KEY = sys.argv[1], sys.argv[2], sys.argv[3]

for ver in (3.3, 3.4, 3.5, 3.2, 3.1):
    print(f"\n=== Протокол {ver} ===")
    d = tinytuya.Device(DEV_ID, IP, LOCAL_KEY)
    d.set_version(ver)
    d.set_socketTimeout(6)
    try:
        data = d.status()
        err = data.get("Error") if isinstance(data, dict) else None
        if err:
            print(f"  ответ с ошибкой: {data}")
        elif isinstance(data, dict) and data.get("dps"):
            print(f"  УСПЕХ! Устройство ответило, DP: {data['dps']}")
            print(f"\n>>> Рабочая версия протокола: {ver} <<<")
            break
        else:
            print(f"  странный ответ: {data}")
    except Exception as e:
        print(f"  нет ответа: {type(e).__name__}: {e}")
else:
    print("\nНи одна версия не ответила.")
    print("Проверьте: 1) ping до устройства, 2) Smart Life закрыт везде,")
    print("3) перезагрузка контроллера по питанию, 4) local_key без опечаток.")
