import datetime
import time
from decimal import *

from django.db.models import Q
from django.http import Http404
from django.views.generic import list_detail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.forms.models import inlineformset_factory, modelformset_factory
from django.db.models import Q
from django.contrib.sites.models import Site
from django.utils import simplejson
#from django.views.decorators.csrf import csrf_protect

from distribution.models import *
from producer.forms import *
from producer.view_helpers import *
from distribution.forms import DateRangeSelectionForm, DeliveryDateForm
from distribution.view_helpers import plan_weeks, create_weekly_plan_forms, SupplyDemandTable

try:
    from notification import models as notification
except ImportError:
    notification = None

def get_producer(request):
    try:
        pc = request.user.producer_contact
        return pc.producer
    except ProducerContact.DoesNotExist:
        return None

def producer_dashboard(request):
    fn = food_network()
    producer = get_producer(request)
    return render_to_response('producer/producer_dashboard.html', 
        {'producer': producer,
         'food_network': fn,
         }, context_instance=RequestContext(request))

def producer_profile(request):
    producer = get_producer(request)
    td = datetime.date.today()
    start = td + datetime.timedelta(weeks=1)
    end = (start + datetime.timedelta(weeks=4)).strftime('%Y_%m_%d')
    start = start.strftime('%Y_%m_%d')
    dcs = DeliveryCycle.objects.all()
    ndc = None
    inventory_closing = td
    for dc in dcs:
        dd = dc.next_delivery_date_using_inventory_closing()
        if dd > td:
            ndc = dc
            break
    if ndc:
        inventory_closing = ndc.inventory_closing(dd)
    return render_to_response('producer/profile.html', 
        {'producer': producer,
         'date': datetime.date.today(),
         'start': start,
         'end': end,
         'inventory_closing': inventory_closing,
         }, context_instance=RequestContext(request))

def edit_producer_profile(request):
    producer = get_producer(request)
    form = ProducerProfileForm(data=request.POST or None, instance=producer)
    ContactFormSet = inlineformset_factory(Producer, ProducerContact, 
        form=ProducerContactForm,
        extra=2)
    formset = ContactFormSet(data=request.POST or None, instance=producer)
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if form.is_valid():
            form.save()
            if formset.is_valid():
                formset.save()
                return HttpResponseRedirect("/producer/profile")
    return render_to_response('producer/profile_edit.html', 
        {'producer': producer,
         'form': form,
         'formset': formset,
         }, context_instance=RequestContext(request))

def edit_producer_products(request):
    producer = get_producer(request)
    fn = food_network()
    ProducerProductFormSet = inlineformset_factory(Producer, ProducerProduct, 
        fk_name="producer",
        form=ProducerProductForm,
        extra=2)
    formset = ProducerProductFormSet(
        data=request.POST or None,
        instance=producer)
    other_prices = comparative_prices(producer)
    price_change_date = fn.next_delivery_date_using_inventory_closing()
    td = datetime.date.today()
    #dcs = DeliveryCycle.objects.all()
    #ndc = None
    #price_change_date = td
    #for dc in dcs:
    #    dd = dc.next_delivery_date_using_inventory_closing()
    #    if dd > td:
    #        ndc = dc
    #        price_change_date = dd
    #        break
    #forms = create_producer_product_forms(producer, data=request.POST or None)
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if formset.is_valid():
            saved_pps = formset.save(commit=False)
            for pp in saved_pps:
                id = pp.id
                price = pp.producer_price
                if id:
                    prev = ProducerProduct.objects.get(id=id)
                    prev_price = prev.producer_price
                    if price != prev_price:
                        pp.price_change_delivery_date = price_change_date
                        pp.price_changed_by = request.user
                        ppc = ProducerPriceChange(
                            producer_product=pp,
                            producer_price=prev_price,
                            price_change_delivery_date=prev.price_change_delivery_date,
                            changed_by=request.user,
                            when_changed=datetime.datetime.now(),
                        )
                        ppc.save()
                else:
                    pp.price_change_delivery_date = td
                    pp.price_changed_by = request.user
                pp.save()
            return HttpResponseRedirect("/producer/profile")
    return render_to_response('producer/products_edit.html', 
        {'producer': producer,
         'formset': formset,
         'comparative_prices': other_prices,
         'fn': fn,
         'price_change_date': price_change_date,
         #'forms': forms,
         }, context_instance=RequestContext(request))

@login_required
def inventory_selection(request):
    #avail_date = next_delivery_date()
    avail_date = datetime.date.today()
    init = {"next_delivery_date": avail_date,}
    producer = get_producer(request)
    form = DeliveryDateForm(data=request.POST or None, initial=init)
    avail = InventoryItem.objects.filter(
        producer=producer,
        remaining__gt=0,
        inventory_date__lte=avail_date,
        expiration_date__gt=avail_date)
    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data
            inv_date = data['next_delivery_date']
            return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
               % ('producer/inventoryupdate', producer.id, inv_date.year, inv_date.month, inv_date.day))
    return render_to_response('producer/inventory_selection.html', {
        'form': form,
        'available': avail,
    }, context_instance=RequestContext(request))

@login_required
def inventory_update(request, prod_id, year, month, day,
            next=None):
    availdate = datetime.date(int(year), int(month), int(day))
    try:
        producer = Party.objects.get(pk=prod_id)
    except Party.DoesNotExist:
        raise Http404
    if request.method == "POST":
        itemforms = create_inventory_item_forms(producer, availdate, request.POST)
        #import pdb; pdb.set_trace()
        if all([itemform.is_valid() for itemform in itemforms]):
            producer_id = request.POST['producer-id']
            producer = Producer.objects.get(pk=producer_id)
            inv_date = request.POST['avail-date']
            for itemform in itemforms:
                data = itemform.cleaned_data
                prod_id = data['prod_id']
                item_id = data['item_id']
                custodian = data['custodian']
                inventory_date = data['inventory_date']
                expiration_date = data['expiration_date']
                remaining = data['remaining']
                notes = data['notes']
                field_id = data['field_id']
                freeform_lot_id = data['freeform_lot_id']

                if item_id:
                    item = InventoryItem.objects.get(pk=item_id)
                    item.custodian = custodian
                    item.inventory_date = inventory_date
                    item.expiration_date = expiration_date
                    rem_change = remaining - item.remaining
                    item.remaining = remaining
                    if not item.deliveries():
                        item.planned = item.planned + rem_change
                    item.notes = notes
                    item.field_id = field_id
                    item.freeform_lot_id = freeform_lot_id
                    item.save()
                else:
                    if remaining > 0:
                        prod_id = data['prod_id']
                        product = Product.objects.get(pk=prod_id)
                        item = itemform.save(commit=False)
                        item.producer = producer
                        item.custodian = custodian
                        item.inventory_date = inventory_date
                        item.expiration_date = expiration_date
                        item.product = product
                        item.planned = remaining
                        item.notes = notes
                        item.field_id = field_id
                        item.freeform_lot_id = freeform_lot_id
                        item.save()
            if next:
                next = next = "".join(["/producer/", next, "/"])
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
                    % ('producer/produceravail', producer_id, year, month, day))
    else:
        itemforms = create_inventory_item_forms(producer, availdate)
    return render_to_response('producer/inventory_update.html', {
        'avail_date': availdate, 
        'producer': producer, 
        'item_forms': itemforms,
        'tabnav': "producer/producer_tabnav.html",
    }, context_instance=RequestContext(request))

@login_required
def produceravail(request, prod_id, year, month, day):
    availdate = datetime.date(int(year), int(month), int(day))
    #availdate = availdate - datetime.timedelta(days=datetime.date.weekday(availdate)) + datetime.timedelta(days=2)
    #weekstart = availdate - datetime.timedelta(days=datetime.date.weekday(availdate))
    try:
        producer = Party.objects.get(pk=prod_id)
        #inventory = InventoryItem.objects.filter(
        #    producer=producer,
        #    inventory_date__range=(weekstart, availdate)
        #)
        inventory = InventoryItem.objects.filter(
            producer=producer,
            remaining__gt=0,
            inventory_date__lte=availdate,
            expiration_date__gt=availdate)
            #Q(producer=producer) &
            #(Q(onhand__gt=0) | Q(inventory_date__range=(weekstart, availdate))))
    except Party.DoesNotExist:
        raise Http404
    return render_to_response('producer/producer_avail.html', 
        {'producer': producer, 
         'avail_date': availdate, 
         'inventory': inventory }, context_instance=RequestContext(request))

@login_required
def process_selection(request):
    process_date = next_delivery_date()
    monday = process_date - datetime.timedelta(days=datetime.date.weekday(process_date))
    saturday = monday + datetime.timedelta(days=5)
    initial_data = {"process_date": process_date}
    processes = Process.objects.filter(process_date__range=(monday, saturday))
    psform = ProcessSelectionForm(data=request.POST or None, initial=initial_data)
    if request.method == "POST":
        if psform.is_valid():
            data = psform.cleaned_data
            process_date = data['process_date']
            process_type_id = data['process_type']
            return HttpResponseRedirect('/%s/%s/'
               % ('producer/newprocess', process_type_id))
    return render_to_response('producer/process_selection.html', {
        'process_date': process_date,
        'header_form': psform,
        'processes': processes,}, context_instance=RequestContext(request))

from distribution.forms import InputLotSelectionForm, InputLotCreationForm, OutputLotCreationFormsetForm

@login_required
def new_process(request, process_type_id):
    try:
        foodnet = food_network()
    except FoodNetwork.DoesNotExist:
        return render_to_response('distribution/network_error.html')
    process_manager = get_producer(request)

    weekstart = next_delivery_date()
    weekend = weekstart + datetime.timedelta(days=5)
    expired_date = weekstart + datetime.timedelta(days=5)
    pt = get_object_or_404(ProcessType, id=process_type_id)

    input_types = pt.input_type.stockable_children()
    input_select_form = None
    input_create_form = None
    input_lot_qties = []
    if pt.use_existing_input_lot:
        input_lots = InventoryItem.objects.filter(
            product__in=input_types, 
            inventory_date__lte=weekend,
            expiration_date__gte=expired_date,
            remaining__gt=Decimal("0"))
        initial_data = {"quantity": Decimal("0")}

        for lot in input_lots:
            input_lot_qties.append([lot.id, float(lot.avail_qty())])
        if input_lots:
            initial_data = {"quantity": input_lots[0].remaining,}
        input_select_form = InputLotSelectionForm(input_lots, data=request.POST or None, prefix="inputselection", initial=initial_data)
    else:
        input_create_form = InputLotCreationForm(input_types, data=request.POST or None, prefix="inputcreation")

    # todo: default service provider to process_manager?
    service_label = "Processing Service"
    service_formset = None
    steps = pt.number_of_processing_steps
    if steps > 1:
        service_label = "Processing Services"
    ServiceFormSet = formset_factory(ProcessServiceForm, extra=0)
    initial_data = []
    for x in range(steps):
        initial_data.append({"from_whom": process_manager.id})
    #print "initial_data", initial_data
    service_formset = ServiceFormSet(
        data=request.POST or None, 
        prefix="service",
        initial=initial_data,
    )

    output_types = pt.output_type.stockable_children()

    output_label = "Output Lot"
    output_formset = None
    outputs = pt.number_of_output_lots
    if outputs > 1:
        output_label = "Output Lots"
    OutputFormSet = formset_factory(OutputLotCreationFormsetForm, extra=outputs)
    output_formset = OutputFormSet(data=request.POST or None, prefix="output")
    for form in output_formset.forms:
        form.fields['product'].choices = [(prod.id, prod.long_name) for prod in output_types]

    process = None

    if request.method == "POST":
        #import pdb; pdb.set_trace()
        if input_create_form:
            if input_create_form.is_valid():
                data = input_create_form.cleaned_data
                lot = input_create_form.save(commit=False)
                producer = data["producer"]
                qty = data["planned"]
                process = Process(
                    process_type = pt,
                    process_date = weekstart,
                    managed_by = process_manager,
                )
                process.save()
                lot.inventory_date = weekstart
                lot.remaining = qty
                lot.save()
                issue = InventoryTransaction(
                    transaction_type = "Issue",
                    process = process,
                    # todo: is to_whom correct in all these process tx?
                    from_whom = producer, 
                    to_whom = producer, 
                    inventory_item = lot,
                    transaction_date = weekstart,
                    amount = qty)
                issue.save()

        elif input_select_form:
            if input_select_form.is_valid():
                data = input_select_form.cleaned_data
                lot_id = data['lot']
                lot = InventoryItem.objects.get(id=lot_id)
                producer = lot.producer
                qty = data["quantity"]
                process = Process(
                    process_type = pt,
                    process_date = weekstart,
                    managed_by = process_manager,
                )
                process.save()
                issue = InventoryTransaction(
                    transaction_type = "Issue",
                    process = process,
                    from_whom = producer, 
                    to_whom = producer, 
                    inventory_item = lot,
                    transaction_date = weekstart,
                    amount = qty)
                issue.save()

        if process:
            if service_formset:
                 # todo: shd be selective, or not?
                if service_formset.is_valid():
                    for service_form in service_formset.forms:
                        tx = service_form.save(commit=False)
                        tx.to_whom = foodnet
                        tx.process = process
                        tx.transaction_date = weekstart
                        tx.save()
            #import pdb; pdb.set_trace()
            if output_formset:
                for form in output_formset.forms:
                    if form.is_valid():
                        data = form.cleaned_data
                        qty = data["planned"]
                        if qty:
                            lot = form.save(commit=False)
                            producer = data["producer"]
                            lot.inventory_date = weekstart
                            lot.save()
                            tx = InventoryTransaction(
                                transaction_type = "Production",
                                process = process,
                                from_whom = producer, 
                                to_whom = producer, 
                                inventory_item = lot,
                                transaction_date = weekstart,
                                amount = qty)
                            tx.save()

            return HttpResponseRedirect('/%s/%s/'
               % ('producer/process', process.id))

    return render_to_response('distribution/new_process.html', {
        'input_lot_qties': input_lot_qties,
        'input_select_form': input_select_form,
        'input_create_form': input_create_form,
        'service_formset': service_formset,
        'service_label': service_label,
        'output_formset': output_formset,
        'output_label': output_label,
        'tabnav': "producer/producer_tabnav.html",
        }, context_instance=RequestContext(request))

@login_required
def process(request, process_id):
    process = get_object_or_404(Process, id=process_id)
    return render_to_response('producer/process.html', 
        {"process": process,}, context_instance=RequestContext(request))

@login_required
def delete_process_confirmation(request, process_id):
    if request.method == "POST":
        process = get_object_or_404(Process, id=process_id)
        outputs = []
        outputs_with_lot = []
        for output in process.outputs():
            lot = output.inventory_item
            qty = output.amount
            if lot.planned == qty:
                outputs_with_lot.append(output)
            else:
                outputs.append(output)
        inputs = []
        inputs_with_lot = []
        for inp in process.inputs():
            lot = inp.inventory_item
            qty = inp.amount
            if lot.planned == qty:
                inputs_with_lot.append(inp)
            else:
                inputs.append(inp)
        return render_to_response('producer/process_delete_confirmation.html', {
            "process": process,
            "outputs": outputs,
            "inputs": inputs,
            "outputs_with_lot": outputs_with_lot,
            "inputs_with_lot": inputs_with_lot,
            }, context_instance=RequestContext(request))

@login_required
def delete_process(request, process_id):
    if request.method == "POST":
        process = get_object_or_404(Process, id=process_id)
        for output in process.outputs():
            lot = output.inventory_item
            qty = output.amount
            output.delete()
            if lot.planned == qty:
                lot.delete()
        for inp in process.inputs():
            lot = inp.inventory_item
            qty = inp.amount
            inp.delete()
            if lot.planned == qty:
                lot.delete()
        for service in process.services():
            service.delete() 
        process.delete()
        #todo: retest, this might not work! 
        return HttpResponseRedirect(reverse("producer_process_selection"))


#@login_required
def plan_selection(request):
    #import pdb; pdb.set_trace()
    from_date = datetime.date.today()
    # force from_date to Monday, to_date to Sunday
    from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
    to_date = from_date + datetime.timedelta(weeks=16)
    to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
    to_date = to_date + datetime.timedelta(days=7)
    plan_init = {
        'plan_from_date': from_date,
        'plan_to_date': to_date,
        'list_type': 'M',
    }
    init = {
        'from_date': from_date,
        'to_date': to_date,
    }
    member = get_producer(request)
    member_has_plans = False
    plans = ProductPlan.objects.filter(member=member)
    if plans.count():
        member_has_plans = True

    if request.method == "POST":
        if request.POST.get('submit-supply-demand'):
            sdform = DateRangeSelectionForm(prefix='sd', data=request.POST)  
            if sdform.is_valid():
                data = sdform.cleaned_data
                from_date = data['from_date'].strftime('%Y_%m_%d')
                to_date = data['to_date'].strftime('%Y_%m_%d')
                return HttpResponseRedirect('/%s/%s/%s/'
                    % ('producer/dojosupplydemand', from_date, to_date))
            else:
                psform = PlanSelectionForm(initial=plan_init)
                income_form = DateRangeSelectionForm(prefix = 'inc', initial=init)

        elif request.POST.get('submit-income'):
            income_form = DateRangeSelectionForm(prefix='inc', data=request.POST)  
            if income_form.is_valid():
                data = income_form.cleaned_data
                from_date = data['from_date'].strftime('%Y_%m_%d')
                to_date = data['to_date'].strftime('%Y_%m_%d')
                return HttpResponseRedirect('/%s/%s/%s/'
                    % ('producer/dojoincome', from_date, to_date))
            else:
                psform = PlanSelectionForm(initial=plan_init)
                sdform = DateRangeSelectionForm(prefix='sd', initial=init)
      
        else:
            psform = PlanSelectionForm(request.POST)  
            if psform.is_valid():
                psdata = psform.cleaned_data
                from_date = psdata['plan_from_date'].strftime('%Y_%m_%d')
                to_date = psdata['plan_to_date'].strftime('%Y_%m_%d')
                list_type = psdata['list_type']
                #return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
                #   % ('producer/planningtable', member.id, list_type, from_date, to_date))
                return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
                   % ('producer/dojoplanningtable', member.id, list_type, from_date, to_date))
            else:
                sdform = DateRangeSelectionForm(prefix='sd', initial=init)
                income_form = DateRangeSelectionForm(prefix = 'inc', initial=init)

    else:
        psform = PlanSelectionForm(initial=plan_init)
        sdform = DateRangeSelectionForm(prefix='sd', initial=init)
        income_form = DateRangeSelectionForm(prefix = 'inc', initial=init)
    return render_to_response('producer/plan_selection.html', 
            {'plan_form': psform,
             'sdform': sdform,
             'income_form': income_form,
             'member_has_plans': member_has_plans,
            }, context_instance=RequestContext(request))

@login_required
def planning_table(request, member_id, list_type, from_date, to_date):
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    role = "producer"
    plan_type = "Production"
    if member.is_customer():
        role = "consumer"
        plan_type = "Consumption"

    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    # force from_date to Monday, to_date to Sunday
    from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
    to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
    to_date = to_date + datetime.timedelta(days=7)
    products = None
    if list_type == "M":
        if role == "consumer":
            products = CustomerProduct.objects.filter(customer=member, planned=True)
        else:
            products = ProducerProduct.objects.filter(producer=member, planned=True)
    if not products:
        products = Product.objects.filter(plannable=True)
        list_type = "A"
    plan_table = plan_weeks(member, products, from_date, to_date)
    forms = create_weekly_plan_forms(plan_table.rows, data=request.POST or None)
    if request.method == "POST":
        for row in forms:
            if row.formset.is_valid():
                for form in row.formset.forms:
                    data = form.cleaned_data
                    qty = data['quantity']
                    plan_id = data['plan_id']
                    from_dt = data['from_date']
                    to_dt = data['to_date']
                    product_id = data['product_id']
                    plan = None
                    if plan_id:
                        # what if plan was changed by prev cell?
                        plan = ProductPlan.objects.get(id=plan_id)
                        if plan.to_date < from_dt or plan.from_date > to_dt:
                            plan = None
                    if qty:
                        if plan:
                            if not qty == plan.quantity:
                                if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                    plan.quantity = qty
                                    plan.save()
                                else:
                                    if plan.from_date < from_dt:
                                        new_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=plan.from_date,
                                            to_date=new_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        earlier_plan.save()
                                    if plan.to_date > to_dt:
                                        new_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=qty,
                                            from_date=from_dt,
                                            to_date=to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        new_plan.save()
                                        plan.from_date = to_dt + datetime.timedelta(days=1)
                                        plan.save()
                                    else:
                                        plan.from_date=from_dt
                                        plan.quantity=qty
                                        plan.save()      
                        else:
                            product = Product.objects.get(id=product_id)
                            new_plan = ProductPlan(
                                member=member,
                                product=product,
                                quantity=qty,
                                from_date=from_dt,
                                to_date=to_dt,
                                role=role,
                            )
                            new_plan.save()
                            if role == "producer":
                                listed_product, created = ProducerProduct.objects.get_or_create(
                                    product=product, producer=member)
                            #elif role == "consumer":
                            #    listed_product, created = CustomerProduct.objects.get_or_create(
                            #        product=product, customer=member)

                    else:
                        if plan:
                            if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                plan.delete()
                            else:
                                if plan.to_date > to_dt:
                                    early_from_dt = plan.from_date              
                                    if plan.from_date < from_dt:
                                        early_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=early_from_dt,
                                            to_date=early_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                         )
                                        earlier_plan.save()
                                    plan.from_date = to_dt + datetime.timedelta(days=1)
                                    plan.save()
                                else:
                                    plan.to_date= from_dt - datetime.timedelta(days=1)
                                    plan.save()
        from_date = from_date.strftime('%Y_%m_%d')
        to_date = to_date.strftime('%Y_%m_%d')
        return HttpResponseRedirect('/%s/%s/%s/%s/'
                    % ('producer/producerplans', from_date, to_date, member_id))
    return render_to_response('distribution/planning_table.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'plan_table': plan_table,
            'forms': forms,
            'plan_type': plan_type,
            'member': member,
            'list_type': list_type,
            'tabnav': "producer/producer_tabnav.html",
        }, context_instance=RequestContext(request))

@login_required
def dojo_planning_table(request, member_id, list_type, from_date, to_date,
        next=None):
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    role = "producer"
    plan_type = "Production"
    if member.is_customer():
        role = "consumer"
        plan_type = "Consumption"
    from_datestring = from_date
    to_datestring = to_date
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    # force from_date to Monday, to_date to Sunday
    from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
    to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
    to_date = to_date + datetime.timedelta(days=7)
    products = None
    if list_type == "M":
        if role == "consumer":
            products = CustomerProduct.objects.filter(customer=member, planned=True)
        else:
            products = ProducerProduct.objects.filter(producer=member, planned=True)
    if not products:
        products = Product.objects.filter(plannable=True)
        list_type = "A"
    columns = plan_columns(from_date, to_date)
    return render_to_response('producer/dojo_planning_table.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'from_datestring': from_datestring,
            'to_datestring': to_datestring,
            'columns': columns,
            'column_count': len(columns),
            'plan_type': plan_type,
            'member': member,
            'list_type': list_type,
            'next': next,
            'tabnav': "producer/producer_tabnav.html",
        }, context_instance=RequestContext(request))


def json_planning_table(request, member_id, list_type, from_date, to_date, row_id=None):
    #import pdb; pdb.set_trace()
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    role = "producer"
    plan_type = "Production"
    if member.is_customer():
        role = "consumer"
        plan_type = "Consumption"

    #import pdb; pdb.set_trace()
    if row_id:
        if request.method == "GET":
            #import pdb; pdb.set_trace()
            response = HttpResponse(request.raw_post_data, mimetype="text/json-comment-filtered")
            response['Cache-Control'] = 'no-cache'
            return response
        elif request.method == "PUT":
            #import pdb; pdb.set_trace()
            product = Product.objects.get(id=row_id)
            data = simplejson.loads(request.raw_post_data)
            member = Party.objects.get(id=data['member_id'])
            fd = data["from_date"]
            td = data["to_date"]
            from_date = datetime.datetime(*time.strptime(fd, '%Y-%m-%d')[0:5]).date()
            to_date = datetime.datetime(*time.strptime(td, '%Y-%m-%d')[0:5]).date() 
            wkdate = from_date
            while wkdate <= to_date:
                key = wkdate.strftime('%Y-%m-%d')
                qty = data[key]
                if is_number(qty):
                    qty = Decimal(qty)
                    plan_id = data.get(":".join([key, "plan_id"]))
                    from_dt = wkdate
                    to_dt = from_dt + datetime.timedelta(days=6)
                    plan = None
                    if plan_id:
                        plan = ProductPlan.objects.get(id=plan_id)
                        if plan.to_date < from_dt or plan.from_date > to_dt:
                            plan = None
                    if qty:
                        if plan:
                            if not qty == plan.quantity:
                                if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                    plan.quantity = qty
                                    plan.save()
                                else:
                                    if plan.from_date < from_dt:
                                        new_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=plan.from_date,
                                            to_date=new_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        earlier_plan.save()
                                    if plan.to_date > to_dt:
                                        new_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=qty,
                                            from_date=from_dt,
                                            to_date=to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        new_plan.save()
                                        plan.from_date = to_dt + datetime.timedelta(days=1)
                                        plan.save()
                                    else:
                                        plan.from_date=from_dt
                                        plan.quantity=qty
                                        plan.save()      
                        else:
                            new_plan = ProductPlan(
                                member=member,
                                product=product,
                                quantity=qty,
                                from_date=from_dt,
                                to_date=to_dt,
                                role=role,
                            )
                            new_plan.save()
                            if role == "producer":
                                listed_product, created = ProducerProduct.objects.get_or_create(
                                    product=product, producer=member)
                            elif role == "consumer":
                                listed_product, created = CustomerProduct.objects.get_or_create(
                                    product=product, customer=member)

                    else:
                        if plan:
                            if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                plan.delete()
                            else:
                                if plan.to_date > to_dt:
                                    early_from_dt = plan.from_date              
                                    if plan.from_date < from_dt:
                                        early_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=early_from_dt,
                                            to_date=early_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                         )
                                        earlier_plan.save()
                                    plan.from_date = to_dt + datetime.timedelta(days=1)
                                    plan.save()
                                else:
                                    plan.to_date= from_dt - datetime.timedelta(days=1)
                                    plan.save()

                wkdate = wkdate + datetime.timedelta(days=7)

            response = HttpResponse(request.raw_post_data, mimetype="text/json-comment-filtered")
            response['Cache-Control'] = 'no-cache'
            return response
    else:
        try:
            from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
            to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
        except ValueError:
            raise Http404
        # force from_date to Monday, to_date to Sunday
        from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
        to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
        to_date = to_date + datetime.timedelta(days=7)
        products = None
        if list_type == "M":
            if role == "consumer":
                products = CustomerProduct.objects.filter(customer=member, planned=True)
            else:
                products = ProducerProduct.objects.filter(producer=member, planned=True)
        if not products:
            products = Product.objects.filter(plannable=True)
            list_type = "A"
        #import pdb; pdb.set_trace()
        rows = plans_for_dojo(member, products, from_date, to_date)
        range = request.META["HTTP_RANGE"]
        range = range.split("=")[1]
        range = range.split("-")
        range_start = int(range[0])
        range_end = int(range[1])
        count = len(rows)
        if count < range_end:
            range_end = count
        rows = rows[range_start:range_end + 1]
        data = simplejson.dumps(rows)
        response = HttpResponse(data, mimetype="text/json-comment-filtered")
        response['Cache-Control'] = 'no-cache'
        response['Content-Range'] = "".join(["items ", str(range_start),
            "-", str(range_end), "/", str(count + 1)])
        return response

@login_required
def dojo_member_plans(request, from_date, to_date, member_id):
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    from_datestring = from_date
    to_datestring = to_date
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    #sdtable = supply_demand_table(from_date, to_date, member)
    if member.is_customer():
        plan_type = "Consumption"
        products = CustomerProduct.objects.filter(customer=member, planned=True)
    else:
        plan_type = "Production"
        products = ProducerProduct.objects.filter(producer=member, planned=True)
    columns = plan_columns(from_date, to_date)
    return render_to_response('distribution/dojo_member_plans.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'columns': columns,
            'column_count': len(columns),
            'member': member,
            'from_datestring': from_datestring,
            'to_datestring': to_datestring,
            'plan_type': plan_type,
            'tabnav': "producer/producer_tabnav.html",
        }, context_instance=RequestContext(request))

@login_required
def json_member_plans(request, from_date, to_date, member_id):
    #import pdb; pdb.set_trace()
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    if member.is_customer():
        plan_type = "Consumption"
        products = CustomerProduct.objects.filter(customer=member, planned=True)
    else:
        plan_type = "Production"
        #products = ProducerProduct.objects.filter(producer=member, planned=True)
        products = [plan.product for plan in
                    ProductPlan.objects.filter(member=member)]
        products = list(set(products))

    rows = plans_for_dojo(member, products, from_date, to_date)
    count = len(rows)
    try:
        range = request.META["HTTP_RANGE"]
        range = range.split("=")[1]
        range = range.split("-")
        range_start = int(range[0])
        range_end = int(range[1])
    except KeyError:
        range_start = 0
        range_end = count
    if count < range_end:
        range_end = count
    rows = rows[range_start:range_end + 1]
    data = simplejson.dumps(rows)
    response = HttpResponse(data, mimetype="text/json-comment-filtered")
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = "".join(["items ", str(range_start),
        "-", str(range_end), "/", str(count + 1)])
    return response

@login_required
def dojo_supply_and_demand(request, from_date, to_date):
    from_datestring = from_date
    to_datestring = to_date
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    columns = sd_columns(from_date, to_date)
    return render_to_response('distribution/dojo_supply_demand.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'from_datestring': from_datestring,
            'to_datestring': to_datestring,
            'columns': columns,
            'column_count': len(columns),
            'tabnav': "producer/producer_tabnav.html",
            'tabs': 'P',
        }, context_instance=RequestContext(request))

@login_required
def json_supply_and_demand(request, from_date, to_date):
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    rows = supply_demand_rows(from_date, to_date)
    count = len(rows)
    try:
        range = request.META["HTTP_RANGE"]
        range = range.split("=")[1]
        range = range.split("-")
        range_start = int(range[0])
        range_end = int(range[1])
    except KeyError:
        range_start = 0
        range_end = count
    if count < range_end:
        range_end = count
    rows = rows[range_start:range_end + 1]
    data = simplejson.dumps(rows)
    response = HttpResponse(data, mimetype="text/json-comment-filtered")
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = "".join(["items ", str(range_start),
        "-", str(range_end), "/", str(count + 1)])
    return response

@login_required
def dojo_supply_and_demand_week(request, tabs, week_date):
    try:
        week_date = datetime.datetime(*time.strptime(week_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    sdtable = dojo_supply_demand_weekly_table(week_date)
    columns = sdtable.columns
    tabnav = "distribution/tabnav.html"
    if tabs == "P":
        tabnav = "producer/producer_tabnav.html"
    return render_to_response('distribution/dojo_supply_demand_week.html', 
        {
            'week_date': week_date,
            'columns': columns,
            'column_count': len(columns),
            'tabnav': tabnav,
        }, context_instance=RequestContext(request))

@login_required
def dojo_income(request, from_date, to_date):
    from_datestring = from_date
    to_datestring = to_date
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    member = get_producer(request)
    income_table = producer_suppliable_demand(from_date, to_date, member)
    total_gross =  sum(row[len(row)-1] for row in income_table.rows)
    columns = sd_columns(from_date, to_date)
    return render_to_response('producer/dojo_income.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'member': member,
            'from_datestring': from_datestring,
            'to_datestring': to_datestring,
            'total_gross': total_gross,
            'columns': columns,
            'column_count': len(columns) + 2,
            'tabnav': "producer/producer_tabnav.html",
            'tabs': 'P',
        }, context_instance=RequestContext(request))

@login_required
def json_income(request, from_date, to_date):
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    producer = get_producer(request)
    rows = producer_json_income_rows(from_date, to_date, producer)
    count = len(rows)
    try:
        range = request.META["HTTP_RANGE"]
        range = range.split("=")[1]
        range = range.split("-")
        range_start = int(range[0])
        range_end = int(range[1])
    except KeyError:
        range_start = 0
        range_end = count
    if count < range_end:
        range_end = count
    rows = rows[range_start:range_end + 1]
    data = simplejson.dumps(rows)
    response = HttpResponse(data, mimetype="text/json-comment-filtered")
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = "".join(["items ", str(range_start),
        "-", str(range_end), "/", str(count + 1)])
    return response



@login_required
def supply_and_demand(request, from_date, to_date):
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    member = get_producer(request)
    sdtable = supply_demand_table(from_date, to_date, member)
    return render_to_response('distribution/supply_demand.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'sdtable': sdtable,
            'tabnav': "producer/producer_tabnav.html",
            'tabs': 'P',
        }, context_instance=RequestContext(request))

@login_required
def income(request, from_date, to_date):
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    member = get_producer(request)
    income_table = producer_suppliable_demand(from_date, to_date, member)
    total_income =  sum(row[len(row)-1] for row in income_table.rows)
    return render_to_response('producer/producer_income.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'total_income': total_income,
            'income_table': income_table,
        }, context_instance=RequestContext(request))

@login_required
def member_supply_and_demand(request, from_date, to_date, member_id):
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    sdtable = producer_plans_table(from_date, to_date, member)
    plan_type = "Production"
    if member.is_customer():
        plan_type = "Consumption"
    #import pdb; pdb.set_trace()
    return render_to_response('distribution/member_plans.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'sdtable': sdtable,
            'member': member,
            'plan_type': plan_type,
            'tabnav': "producer/producer_tabnav.html", 
        }, context_instance=RequestContext(request))


