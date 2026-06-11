# tests/test_security.py
import requests, time, pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.demoblaze.com'

SQL_PAYLOADS = [
    ("' OR '1'='1", "Классическая инъекция (всегда истина)"),
    ("' OR 1=1 --", "Комментарий после условия"),
    ("admin'--", "Обход пароля через комментарий"),
    ("' UNION SELECT 1--", "UNION-инъекция"),
    ("'; DROP TABLE users--", "Попытка удаления таблицы"),
]

WEAK_PASSWORDS = [
    ('123', 'Слишком короткий (3 символа)'),
    ('password', 'Распространённый словарный пароль'),
    ('12345678', 'Только цифры'),
    ('aaaaaaaaa', 'Повторяющиеся символы'),
    ('user@test', 'Совпадает с именем пользователя'),
]

SECURITY_HEADERS = {
    'X-Frame-Options': 'Защита от clickjacking',
    'X-Content-Type-Options': 'Защита от MIME-sniffing',
    'Strict-Transport-Security': 'HSTS — принудительный HTTPS',
    'Content-Security-Policy': 'Защита от XSS',
    'X-XSS-Protection': 'Встроенная XSS-защита браузера',
    'Referrer-Policy': 'Контроль данных реферера',
}


def test_sql_injection_login(driver):
    """SEC-01: SQL-инъекции в форме входа."""
    results = []
    for payload, desc in SQL_PAYLOADS:
        # Обновляем страницу перед каждым пейлоадом для чистоты эксперимента
        driver.get(BASE)
        time.sleep(1)

        driver.find_element(By.ID, 'login2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'loginusername')))
        driver.find_element(By.ID, 'loginusername').clear()
        driver.find_element(By.ID, 'loginusername').send_keys(payload)
        driver.find_element(By.ID, 'loginpassword').clear()
        driver.find_element(By.ID, 'loginpassword').send_keys('anypassword')
        driver.find_element(By.XPATH, "//button[text()='Log in']").click()

        time.sleep(2)

        # Закрываем алерт об ошибке
        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept()
        except:
            pass

        # Проверяем, что кнопка Log out не только есть, но и ВИДИМА
        logout_elements = driver.find_elements(By.ID, 'logout2')
        logout_visible = len(logout_elements) > 0 and logout_elements[0].is_displayed()

        status = 'УЯЗВИМ' if logout_visible else 'ЗАЩИЩЁН'
        results.append((payload, desc, status))
        driver.save_screenshot(f'report/sec_01_{len(results)}.png')

    print('\n=== SEC-01: Результаты SQL-инъекций ===')
    for p, d, s in results:
        print(f'  {s:10s} | {d:40s} | {repr(p)}')

    # Проверяем, что все попытки отбиты
    assert all(r[2] == 'ЗАЩИЩЁН' for r in results), 'КРИТИЧНО: SQL-инъекция прошла!'


def test_weak_password_registration(driver):
    """SEC-02: Регистрация со слабыми паролями."""
    driver.get(BASE)
    results = []
    for pwd, desc in WEAK_PASSWORDS:
        username = f'testuser_{int(time.time())}_{pwd}'
        driver.find_element(By.ID, 'signin2').click()
        WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((By.ID, 'sign-username')))
        driver.find_element(By.ID, 'sign-username').clear()
        driver.find_element(By.ID, 'sign-username').send_keys(username)
        driver.find_element(By.ID, 'sign-password').clear()
        driver.find_element(By.ID, 'sign-password').send_keys(pwd)
        driver.find_element(By.XPATH, "//button[text()='Sign up']").click()

        time.sleep(2)
        try:
            alert = WebDriverWait(driver, 4).until(EC.alert_is_present())
            msg = alert.text
            alert.accept()
            accepted = 'successful' in msg.lower()
        except:
            accepted = False

        status = 'УЯЗВИМ (принят)' if accepted else 'OK (отклонён)'
        results.append((repr(pwd), desc, status))
        driver.save_screenshot(f'report/sec_02_{len(results)}.png')

    print('\n=== SEC-02: Политика паролей ===')
    for pw, d, s in results:
        print(f'  {s:20s} | {d}')

    assert all('OK' in r[2] for r in results), 'Система принимает слабые пароли!'


def test_security_headers():
    """SEC-03: Проверка защитных HTTP-заголовков."""
    r = requests.get(BASE, timeout=10)
    print('\n=== SEC-03: Заголовки безопасности ===')
    missing = []
    for header, desc in SECURITY_HEADERS.items():
        val = r.headers.get(header, None)
        status = f'[OK] {val}' if val else '[ОТСУТСТВУЕТ]'
        print(f'  {header:35s}: {status}')
        if not val:
            missing.append(header)

    critical = [h for h in missing if h in ['X-Frame-Options', 'X-Content-Type-Options']]
    assert not critical, f'Критичные защитные заголовки отсутствуют: {critical}'