import os
import django
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from shopapp.models import Product, Order


def create_test_users():
    print("Создание тестовых пользователей...")

    users_data = [
        {'username': 'alex_ivanov', 'email': 'alex@example.com', 'first_name': 'Алексей', 'last_name': 'Иванов'},
        {'username': 'maria_petrova', 'email': 'maria@example.com', 'first_name': 'Мария', 'last_name': 'Петрова'},
        {'username': 'sergey_sidorov', 'email': 'sergey@example.com', 'first_name': 'Сергей', 'last_name': 'Сидоров'},
        {'username': 'olga_kuznetsova', 'email': 'olga@example.com', 'first_name': 'Ольга', 'last_name': 'Кузнецова'},
        {'username': 'dmitry_volkov', 'email': 'dmitry@example.com', 'first_name': 'Дмитрий', 'last_name': 'Волков'},
        {'username': 'anna_smirnova', 'email': 'anna@example.com', 'first_name': 'Анна', 'last_name': 'Смирнова'},
        {'username': 'pavel_fedorov', 'email': 'pavel@example.com', 'first_name': 'Павел', 'last_name': 'Федоров'},
        {'username': 'elena_morozova', 'email': 'elena@example.com', 'first_name': 'Елена', 'last_name': 'Морозова'},
        {'username': 'nikolay_vasiliev', 'email': 'nikolay@example.com', 'first_name': 'Николай',
         'last_name': 'Васильев'},
        {'username': 'irina_romanova', 'email': 'irina@example.com', 'first_name': 'Ирина', 'last_name': 'Романова'},
    ]

    created_users = []

    for user_data in users_data:
        # Проверяем, существует ли пользователь
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='test123',  # Простой пароль для тестирования
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            created_users.append(user)
            print(f"✅ Создан пользователь: {user.username}")
        else:
            user = User.objects.get(username=user_data['username'])
            print(f"ℹ️ Пользователь уже существует: {user.username}")
            created_users.append(user)

    # Создаем тестовые товары, если их нет
    if Product.objects.count() == 0:
        print("\nСоздание тестовых товаров...")
        test_products = [
            {
                'name': 'Ноутбук ASUS',
                'description': 'Мощный ноутбук для работы и игр',
                'price': 899.99,
                'discount': 10,
            },
            {
                'name': 'Смартфон iPhone',
                'description': 'Флагманский смартфон',
                'price': 999.99,
                'discount': 5,
            },
            {
                'name': 'Наушники Sony',
                'description': 'Беспроводные наушники с шумоподавлением',
                'price': 299.99,
                'discount': 15,
            },
            {
                'name': 'Клавиатура Logitech',
                'description': 'Механическая клавиатура',
                'price': 129.99,
                'discount': 0,
            },
            {
                'name': 'Монитор Samsung',
                'description': '27-дюймовый 4K монитор',
                'price': 399.99,
                'discount': 20,
            },
        ]

        for product_data in test_products:
            Product.objects.create(**product_data)
            print(f"✅ Создан товар: {product_data['name']}")

    # Создаем тестовые заказы для пользователей
    print("\nСоздание тестовых заказов...")
    products = list(Product.objects.all())

    for i, user in enumerate(created_users[:5]):  # Создаем заказы для первых 5 пользователей
        order = Order.objects.create(
            delivery_address=f'ул. Тестовая, д. {i + 1}, кв. {i + 10}',
            promocode='WELCOME10' if i % 2 == 0 else 'SALE20',
            user=user
        )

        # Добавляем случайные товары в заказ (от 1 до 3 товаров)
        import random
        num_products = random.randint(1, min(3, len(products)))
        selected_products = random.sample(products, num_products)

        for product in selected_products:
            order.products.add(product)

        print(f"✅ Создан заказ #{order.id} для пользователя {user.username} с {num_products} товарами")

    print(f"\n{'=' * 50}")
    print("ГОТОВО!")
    print(f"{'=' * 50}")
    print(f"Создано/найдено пользователей: {len(created_users)}")
    print(f"Товаров в базе: {Product.objects.count()}")
    print(f"Заказов в базе: {Order.objects.count()}")
    print(f"\nДанные для входа:")
    print("  Логин: test_user_1 (или любой другой из списка)")
    print("  Пароль: test123")


if __name__ == '__main__':
    create_test_users()
