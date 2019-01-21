import napkin


@napkin.seq_diagram()
def distributed_control(c):
    """
    Figure 4.2 from UML Distilled 3E
    """
    user = c.object('User')
    order = c.object('Order')
    orderLine = c.object('OrderLine')
    product = c.object('Product')
    customer = c.object('Customer')

    with user:
        with order.calculatePrice():
            with orderLine.calculatePrice():
                product.getPrice('quantity:number')
                with customer.getDiscountedValue(order):
                    order.getBaseValue().ret('value')
                    c.ret('discountedValue')
