from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from fluffyshop.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """
    Представление добавления товаров в корзину, при валидации количество
     товара либо обновляется, либо добавляется.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Представление удаления товара из корзины.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Представление отображения корзины, с обновлением количества товаров.
    Форма инициализируется текущим количеством товаров, и при передаче
    в обработку количество заменяется новым.
    """
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'cart/detail.html',
                  {'cart': cart})



