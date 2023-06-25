from decimal import Decimal
from django.conf import settings
from fluffyshop.models import Product


class Cart:
    def __init__(self, request):
        """
        Инициализация корзины товаров. Сохраняем текущую сессию, получаем корзину из текущего сеанса, если корзины
        не существует - создаем пустую корзину.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Метод добавления товара в корзину.
        :param product: экземпляр product.
        :param quantity: количество товара.
        :param override_quantity: при False - добавляем к существующему количеству, при True - оставляем без
        изменений.
        product_id - ключ в словаре cart, преобразуем в строку, так как JSON допускает использование
        только строковых типов в качестве ключей.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Помечаем сеанс как измененный, чтобы произвести его сохранение.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Удаление товара из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Создаем переменную корзины и копируем в нее все товары, которые соответствуют ключам, добавляем экземпляры
        products в корзину, приводим цену каждого продукта к decimal, добавляем к каждому товару атрибут total price.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет количества позиций в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Получение суммы покупок.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Очистить корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
