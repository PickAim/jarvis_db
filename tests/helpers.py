from jorm.market.items import Product


def sort_product(product: Product):
    for history in product.history:
        for leftovers in history.leftover.values():
            leftovers.sort(key=lambda unit: unit.specify)
            leftovers.sort(key=lambda unit: unit.leftover)
