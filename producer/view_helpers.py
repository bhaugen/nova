from decimal import *

from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from distribution.models import *
from distribution.view_helpers import SupplyDemandTable, SuppliableDemandCell
from producer.forms import *


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def create_producer_product_forms(producer_products, data=None):
    form_list = []
    for pp in producer_products:
        init = {'product_id': pp.product.id,}
        form = ProducerProductEditForm(data, 
            prefix=pp.id, instance=pp, initial=init)
        form.product = pp.product.name_with_method()
        form.min = pp.product.formatted_min_price()
        form.max = pp.product.formatted_max_price()
        form.deletable = pp.is_deletable()
        #form.selling_price = pp.product.selling_price
        #if not pp.is_deletable():
        #    form.fields['delete'] = None
        form_list.append(form)
    return form_list


class ComparativePrice(object):
    def __init__(self, product, producer, price):
         self.product = product
         self.producer = producer
         self.price = price


def comparative_prices(producer):
    pps = producer.producer_products.all()
    prices = []
    fn = food_network()
    for pp in pps:
        product = pp.product
        cps = ProducerProduct.objects.filter(
            product=product).exclude(producer=producer)
        for cp in cps:
            price = cp.producer_price
            if price:
                price = price.quantize(Decimal('.01'), rounding=ROUND_UP)
                cp = ComparativePrice(
                    product=product,
                    producer=cp.producer,
                    price=price,
                )
                prices.append(cp)
    return prices

def create_inventory_item_forms(producer, avail_date, data=None):
    monday = avail_date - datetime.timedelta(days=datetime.date.weekday(avail_date))
    saturday = monday + datetime.timedelta(days=5)
    items = InventoryItem.objects.filter(
        producer=producer,
        remaining__gt=0,
        inventory_date__lte=avail_date,
        expiration_date__gt=avail_date)
    #import pdb; pdb.set_trace()
    item_dict = {}
    plan_dict = {}
    for item in items:
        item_dict[item.product.id] = item
    plans = ProductPlan.objects.filter(
        member=producer, 
        from_date__lte=avail_date, 
        to_date__gte=saturday)
    for plan in plans:
        plan_dict[plan.product.id] = plan
    form_list = []
    for item in items:
        try:
            plan = plan_dict[item.product.id]
            plan_qty = plan.quantity        
        except KeyError:
            planned = 0
        #todo: ordered and remainder logic here does not work correctly
        #needs to be adjusted for ordering by producer - even then, cd be wrong
        ordered = item.product.total_ordered_for_timespan(avail_date, saturday)
        prefix = "".join(["item", str(item.id)])
        the_form = InventoryItemForm(data, prefix=prefix, initial={
            'item_id': item.id,
            'prod_id': item.product.id,
            'freeform_lot_id': item.freeform_lot_id,
            'field_id': item.field_id,
            'custodian': item.custodian,
            'inventory_date': item.inventory_date,
            'expiration_date': item.expiration_date,
            'remaining': item.remaining,
            'notes': item.notes})
        the_form.description = item.product.long_name
        the_form.ordered = ordered
        form_list.append(the_form)
    for plan in plans:
        #import pdb; pdb.set_trace()
        if not plan.product.id in item_dict:
            expiration_date = avail_date + datetime.timedelta(days=plan.product.expiration_days)
            prefix = "".join(["plan", str(plan.id)])
            the_form = InventoryItemForm(data, prefix=prefix, initial={
                'prod_id': plan.product.id, 
                'inventory_date': avail_date,
                'expiration_date': expiration_date,
                'remaining': 0,
                'notes': ''})
            the_form.description = plan.product.long_name
            the_form.ordered = 0
            form_list.append(the_form)
    pps = producer.producer_products.all()
    for pp in pps:
        if not pp.product.id in plan_dict:
            expiration_date = avail_date + datetime.timedelta(days=pp.product.expiration_days)
            prefix = "".join(["pp", str(pp.id)])
            the_form = InventoryItemForm(data, prefix=prefix, initial={
                'prod_id': pp.product.id, 
                'inventory_date': avail_date,
                'expiration_date': expiration_date,
                'remaining': 0,
                'notes': ''})
            the_form.description = pp.product.long_name
            the_form.ordered = 0
            form_list.append(the_form)        
    return form_list 

def supply_demand_table(from_date, to_date, member):
    plans = ProductPlan.objects.all()
    cps = ProducerProduct.objects.filter(
        inventoried=False,
        default_avail_qty__gt=0,
    )
    constants = {}
    for cp in cps:
        constants.setdefault(cp.product, Decimal("0"))
        constants[cp.product] += cp.default_avail_qty
    pps = ProducerProduct.objects.filter(producer=member).values_list("product_id")
    pps = set(id[0] for id in pps)
    rows = {}    
    for plan in plans:
        wkdate = from_date
        product = plan.product.supply_demand_product()
        if product.id in pps:
            constant = Decimal('0')
            cp = constants.get(product)
            if cp:
                constant = cp
            row = []
            while wkdate <= to_date:
                row.append(constant)
                wkdate = wkdate + datetime.timedelta(days=7)
            row.insert(0, product)
            rows.setdefault(product, row)
            wkdate = from_date
            week = 0
            while wkdate <= to_date:
                if plan.from_date <= wkdate and plan.to_date >= wkdate:
                    if plan.role == "producer":
                        rows[product][week + 1] += plan.quantity
                    else:
                        rows[product][week + 1] -= plan.quantity
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

def producer_suppliable_demand(from_date, to_date, producer):
    customer_plans = ProductPlan.objects.filter(role="consumer")
    producer_plans = ProductPlan.objects.filter(member=producer)
    fee = producer.decide_producer_fee()/100
    rows = {}    
    for plan in producer_plans:
        wkdate = from_date
        row = []
        while wkdate <= to_date:
            row.append(SuppliableDemandCell(Decimal("0"), Decimal("0")))
            wkdate = wkdate + datetime.timedelta(days=7)
        product = plan.product.supply_demand_product()

        row.insert(0, product)
        rows.setdefault(product, row)
        wkdate = from_date
        week = 0
        while wkdate <= to_date:
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                rows[product][week + 1].supply += plan.quantity
            wkdate = wkdate + datetime.timedelta(days=7)
            week += 1
    pps = ProducerProduct.objects.filter(producer=producer).values_list("product_id")
    pps = set(id[0] for id in pps)
    for plan in customer_plans:
        wkdate = from_date
        product = plan.product
        if product.id in pps:
            week = 0
            while wkdate <= to_date:
                if plan.from_date <= wkdate and plan.to_date >= wkdate:
                    rows[product][week + 1].demand += plan.quantity
                wkdate = wkdate + datetime.timedelta(days=7)
                week += 1
    rows = rows.values()
    for row in rows:
        for x in range(1, len(row)):
            sd = row[x].suppliable()
            if sd >= 0:
                income = sd * row[0].producer_price
                row[x] = income - (income * fee)
            else:
                row[x] = Decimal("0")
    income_rows = []
    for row in rows:
        total = Decimal("0")
        for x in range(1, len(row)):
            total += row[x]
            row[x] = row[x].quantize(Decimal('.1'), rounding=ROUND_UP)
        if total:
            row.append(total.quantize(Decimal('1.'), rounding=ROUND_UP))
            income_rows.append(row)
    label = "Item\Weeks"
    columns = [label]
    wkdate = from_date
    while wkdate <= to_date:
        columns.append(wkdate)
        wkdate = wkdate + datetime.timedelta(days=7)
    columns.append("Total")
    income_rows.sort(lambda x, y: cmp(x[0].long_name, y[0].short_name))
    sdtable = SupplyDemandTable(columns, income_rows)
    return sdtable

def producer_json_income_rows(from_date, to_date, producer):
    #import pdb; pdb.set_trace()
    customer_plans = ProductPlan.objects.filter(role="consumer")
    producer_plans = ProductPlan.objects.filter(member=producer)
    fee = producer.decide_producer_fee()/100
    rows = {}
    pps = []
    for plan in producer_plans:
        wkdate = from_date
        row = {}
        while wkdate <= to_date:
            row[wkdate.strftime('%Y_%m_%d')] = SuppliableDemandCell(Decimal("0"), Decimal("0"))
            wkdate = wkdate + datetime.timedelta(days=7)
        #product = plan.product.supply_demand_product()
        product = plan.product
        if not product.id in pps:
            pps.append(product.id)
        row["product"] =  product.long_name
        row["id"] = product.id
        row["price"] = product.producer_price
        rows.setdefault(product, row)
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                rows[product][key].supply += plan.quantity
            wkdate = wkdate + datetime.timedelta(days=7)
    #pps = ProducerProduct.objects.filter(producer=producer).values_list("product_id")
    #pps = set(id[0] for id in pps)
    for plan in customer_plans:
        wkdate = from_date
        product = plan.product.supply_demand_product()
        if product.id in pps:
            while wkdate <= to_date:
                key = wkdate.strftime('%Y_%m_%d')
                if plan.from_date <= wkdate and plan.to_date >= wkdate:
                    rows[product][key].demand += plan.quantity
                wkdate = wkdate + datetime.timedelta(days=7)
    rows = rows.values()
    for row in rows:
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            sd = row[key].suppliable()
            if sd >= 0:
                income = sd * row['price']
                row[key] = income - (income * fee)
            else:
                row[key] = Decimal("0")
            wkdate = wkdate + datetime.timedelta(days=7)
    income_rows = []
    for row in rows:
        total = Decimal("0")
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            total += row[key]
            row[key] = str(row[key].quantize(Decimal('.1'), rounding=ROUND_UP))
            wkdate = wkdate + datetime.timedelta(days=7)
        if total:
            total = total.quantize(Decimal('1.'), rounding=ROUND_UP)
            row['total']=str(total)
            row["price"] = str(row["price"])
            income_rows.append(row)
    income_rows.sort(lambda x, y: cmp(x["product"], y["product"]))
    return income_rows

#todo: does not use contants (NIPs)
#or correct logic for storage items
def json_income_rows(from_date, to_date, member=None):
    #import pdb; pdb.set_trace()
    plans = ProductPlan.objects.all()
    if member:
        plans = plans.filter(member=member)
    rows = {}    
    for plan in plans:
        wkdate = from_date
        row = {}
        while wkdate <= to_date:
            row[wkdate.strftime('%Y_%m_%d')] = SuppliableDemandCell(Decimal("0"), Decimal("0"))
            wkdate = wkdate + datetime.timedelta(days=7)
        product = plan.product.supply_demand_product()
        row["product"] =  product.long_name
        row["id"] = product.id
        row["price"] = product.price
        rows.setdefault(product, row)
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                if plan.role == "producer":
                    rows[product][key].supply += plan.quantity
                else:
                    rows[product][key].demand += plan.quantity
            wkdate = wkdate + datetime.timedelta(days=7)
    rows = rows.values()
    cust_fee = customer_fee()
    #import pdb; pdb.set_trace()
    for row in rows:
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            sd = row[key].suppliable()
            if sd > 0:
                income = sd * row["price"]
                row[key] = income
            else:
                row[key] = Decimal("0")
            wkdate = wkdate + datetime.timedelta(days=7)
    income_rows = []
    for row in rows:
        base = Decimal("0")
        total = Decimal("0")
        wkdate = from_date
        while wkdate <= to_date:
            key = wkdate.strftime('%Y_%m_%d')
            cell = row[key]
            base += cell
            cell += cell * cust_fee
            total += cell
            row[key] = str(cell.quantize(Decimal('.1'), rounding=ROUND_UP))
            wkdate = wkdate + datetime.timedelta(days=7)
        if total:
            net = base * cust_fee + (base * producer_fee())
            net = net.quantize(Decimal('1.'), rounding=ROUND_UP)
            total = total.quantize(Decimal('1.'), rounding=ROUND_UP)
            row["total"] = str(total)
            row["net"] = str(net)
            row["price"] = str(row["price"])
            income_rows.append(row)
    income_rows.sort(lambda x, y: cmp(x["product"], y["product"]))
    return income_rows


def producer_plans_table(from_date, to_date, producer):
    plans = ProductPlan.objects.filter(member=producer)
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

def plan_columns(from_date, to_date):
    columns = []
    wkdate = from_date
    while wkdate <= to_date:
        columns.append(wkdate.strftime('%Y-%m-%d'))
        wkdate = wkdate + datetime.timedelta(days=7)
    return columns

def sd_columns(from_date, to_date):
    columns = []
    wkdate = from_date
    while wkdate <= to_date:
        columns.append(wkdate.strftime('%Y_%m_%d'))
        wkdate = wkdate + datetime.timedelta(days=7)
    return columns

def plans_for_dojo(member, products, from_date, to_date):
    #import pdb; pdb.set_trace()
    plans = ProductPlan.objects.filter(member=member)
    rows = {}    
    for pp in products:
        yearly = 0
        try:
            product = pp.product
            yearly = pp.qty_per_year
        except:
            product = pp
        if not yearly:
            try:
                pp = ProducerProduct.objects.get(producer=member, product=product)
                yearly = pp.qty_per_year
            except:
                pass
        wkdate = from_date
        row = {}
        row["product"] = product.long_name
        row["yearly"] = int(yearly)
        row["id"] = product.id
        row["member_id"] = member.id
        row["from_date"] = from_date.strftime('%Y-%m-%d')
        row["to_date"] = to_date.strftime('%Y-%m-%d')
        while wkdate <= to_date:
            enddate = wkdate + datetime.timedelta(days=6)
            row[wkdate.strftime('%Y-%m-%d')] = "0"
            wkdate = enddate + datetime.timedelta(days=1)
        rows.setdefault(product, row)
    #import pdb; pdb.set_trace()
    for plan in plans:
        product = plan.product
        wkdate = from_date
        week = 0
        while wkdate <= to_date:
            enddate = wkdate + datetime.timedelta(days=6)
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                rows[product][wkdate.strftime('%Y-%m-%d')] = str(plan.quantity)
                rows[product][":".join([wkdate.strftime('%Y-%m-%d'), "plan_id"])] = plan.id
            wkdate = wkdate + datetime.timedelta(days=7)
            week += 1
    rows = rows.values()
    rows.sort(lambda x, y: cmp(x["product"], y["product"]))
    return rows


