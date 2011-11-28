from operator import attrgetter

from django.forms.formsets import formset_factory
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from distribution.models import *
from customer.forms import *
from paypal.standard.forms import PayPalPaymentsForm
from pay.models import *
from distribution.view_helpers import SupplyDemandTable


def create_paypal_form(order, return_page='unpaid_invoice'):
    pp_settings = PayPalSettings.objects.all()
    if pp_settings.count():
        pp_settings = pp_settings[0]
    else:
        return None
    domain = Site.objects.get_current().domain
    paypal_dict = {
        "business": pp_settings.business,
        "amount": order.grand_total,
        "item_name": " ".join(["Fifth Season order #", str(order.id)]),
        "invoice": order.id,
        "notify_url": 'http://%s%s' % (domain, reverse('paypal-ipn')),
        "return_url": 'http://%s%s' % (domain, reverse(return_page,
            kwargs={'order_id': order.id})),
        "cancel_return": 'http://%s%s' % (domain, reverse(return_page,
            kwargs={'order_id': order.id})),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    form.use_sandbox = pp_settings.use_sandbox
    return form

def create_new_product_list_forms(data=None):
    #todo: shd these be plannable instead of sellable?
    products = list(Product.objects.filter(sellable=True))
    form_list = []
    for prod in products:
        prod.parents = prod.parent_string()
    products.sort(lambda x, y: cmp(x.parents, y.parents))
    for prod in products:
        #if prod.id == 24:
        #    import pdb; pdb.set_trace()
        initial_data = {'prod_id': prod.id}
        form = CustomerProductForm(data, prefix=prod.id, initial=initial_data)
        form.product_name = " ".join([prod.long_name, prod.growing_method])
        form.category = prod.parents
        form_list.append(form)
    return form_list

def create_order_item_forms(order, product_list, availdate, data=None):
    form_list = []
    item_dict = {}
    items = []
    fn = food_network()
    avail = fn.customer_availability(availdate)
    if order:
        items = order.orderitem_set.all()
        for item in items:
            item_dict[item.product.id] = item
    avail_ids = [prod.product.id for prod in avail]
    for item in items:
        if not item.product.id in avail_ids:
            item.category = item.product.parent_string()
            item.qty = item.product.total_avail_today(availdate)
            avail.append(item)
    avail = sorted(avail, key=attrgetter('category'))
    if product_list:
        listed_products = CustomerProduct.objects.filter(
            product_list=product_list).values_list("product_id")
        listed_products = set(id[0] for id in listed_products)
    prods = []
    for prod in avail:
        ok = True
        if product_list:
            if not prod.product.id in listed_products:
                ok = False
        if ok:
            prods.append(prod)
    for prod in prods:
        try:
            item = item_dict[prod.product.id]
        except KeyError:
            item = False
        if item:
            producers = prod.product.avail_producers(availdate)
            initial_data = {
                'prod_id': prod.product.id,
                'avail': item.product.total_avail_today(availdate),
                'unit_price': item.formatted_unit_price(),
            }
            oiform = OrderItemForm(data, prefix=prod.product.id, instance=item,
                                   initial=initial_data)
            oiform.producers = producers
            oiform.description = prod.product.long_name
            oiform.parents = prod.category
            oiform.growing_method = prod.product.growing_method
            form_list.append(oiform)
        else:
            producers = prod.product.avail_producers(availdate)
            oiform = OrderItemForm(data, prefix=prod.product.id, initial={
                'prod_id': prod.product.id, 
                'avail': prod.qty, 
                'unit_price': prod.price, 
                'quantity': 0})
            oiform.description = prod.product.long_name
            oiform.producers = producers
            oiform.parents = prod.category
            oiform.growing_method = prod.product.growing_method
            form_list.append(oiform)
    return form_list

class DisplayTable(object):
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows


class HistoryRow(object):
    def __init__(self, product, quantity, extended_price):
        self.product = product
        self.quantity = quantity
        self.extended_price = extended_price

    def average_price(self):
        return self.extended_price / self.quantity


def create_history_table(customer, from_date, to_date):
    items = OrderItem.objects.filter(
        order__customer=customer, 
        order__delivery_date__range=(from_date, to_date),
        order__state__contains="Filled"
    )
    row_dict = {}
    for item in items:
        row_dict.setdefault(item.product, HistoryRow(item.product, Decimal("0"),
                                                     Decimal("0")))
        row = row_dict[item.product]
        row.quantity += item.quantity
        row.extended_price += item.extended_price()
    rows = row_dict.values()
    rows.sort(lambda x, y: cmp(x.product.short_name, y.product.short_name))
    return rows

def customer_plans_table(from_date, to_date, customer):
    plans = ProductPlan.objects.filter(member=customer)
    rows = {}    
    for plan in plans:
        wkdate = from_date
        product = plan.product.supply_demand_product()
        row = []
        while wkdate <= to_date:
            row.append(Decimal("0"))
            wkdate = wkdate + datetime.timedelta(days=7)
        row.insert(0, product)
        rows.setdefault(product, row)
        wkdate = from_date
        week = 0
        while wkdate <= to_date:
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                rows[product][week + 1] += plan.quantity
            wkdate = wkdate + datetime.timedelta(days=7)
            week += 1
    label = "Product/Weeks"
    columns = [label]
    wkdate = from_date
    while wkdate <= to_date:
        columns.append(wkdate)
        wkdate = wkdate + datetime.timedelta(days=7)
    rows = rows.values()
    rows.sort(lambda x, y: cmp(x[0].short_name, y[0].short_name))
    sdtable = SupplyDemandTable(columns, rows)
    return sdtable
