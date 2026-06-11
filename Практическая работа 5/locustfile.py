from locust import HttpUser, task, between

class ShopUser(HttpUser):
    wait_time = between(1, 3)  # пауза между запросами пользователя
    host = 'https://www.demoblaze.com'

    @task(3)  # вес 3 — выполняется чаще (главная страница)
    def view_homepage(self):
        with self.client.get('/', catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f'Главная: ожидался 200, получен {r.status_code}')

    @task(2)
    def view_category(self):
        # Пользователь возвращается на главную для выбора категории
        self.client.get('/index.html')

    @task(1)
    def view_product(self):
        # Переход в карточку товара
        self.client.get('/prod.html?idp_=2')

    @task(1)
    def check_cart(self):
        # Переход в корзину
        self.client.get('/cart.html')