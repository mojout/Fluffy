from .cart import Cart


def cart(request):
    """
    Контекст для корзины товаров.
    """
    return {'cart': Cart(request)}
