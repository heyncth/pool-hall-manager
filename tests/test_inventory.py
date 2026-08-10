from poolhall.inventory import consume, create_items, low_stock, restock
import pytest


def test_create_items_defaults():
    items = create_items()
    assert len(items) >= 4


def test_restock():
    items = create_items()
    item = restock(items, "Chalk", 10)
    assert item.quantity > 0


def test_consume():
    items = create_items()
    item = consume(items, "Chalk", 1)
    assert item.quantity == 23


def test_consume_missing_item():
    with pytest.raises(KeyError):
        consume(create_items(), "Nope", 1)


def test_low_stock():
    items = create_items()
    items[0].quantity = 1
    assert items[0] in low_stock(items)

def test_restock_negative_rejected():
    with pytest.raises(ValueError):
        restock(create_items(), "Chalk", -1)
