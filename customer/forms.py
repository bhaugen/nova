from django import forms
from django.db.models.query import QuerySet
from django.conf import settings

import datetime

from distribution.models import *


class CustomerProfileForm(forms.ModelForm):
    long_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
    tag_line = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
    phone = forms.CharField(required=False)
    fax = forms.CharField(required=False)
    email_address = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
    #email_address = forms.CharField(required=False, widget=forms.EmailField)
    website = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
    #website = forms.CharField(required=False, widget=forms.URLField)
    address = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'rows': '4','value': ''}))
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    philosophy = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    storage_capacity = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    background_color = forms.ChoiceField(choices=settings.COLOR_CHOICES)
    logo = forms.ImageField(required=False)

    class Meta:
        model = Customer
        exclude = ('member_id', 'short_name', 
                   'customer_transportation_fee', 'apply_transportation_fee')


class CustomerContactForm(forms.ModelForm): 
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '16', 'value': ''}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    #cell = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '32', 'value': ''}))
    avatar = forms.ImageField(required=False)

    class Meta:
        model = CustomerContact
        exclude = ('login_user', 'cell')


class NewOrderSelectionForm(forms.Form):
    #order_date = forms.DateField(
    #    widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    product_list = forms.ChoiceField()

    def __init__(self, customer, *args, **kwargs):
        super(NewOrderSelectionForm, self).__init__(*args, **kwargs)
        choices = [(plist.id, plist.list_name) for plist in
                   MemberProductList.objects.filter(member=customer)]
        choices.extend([(0, 'All Available Products')])
        self.fields['product_list'].choices = choices

class OrderForm(forms.ModelForm):
    transportation_fee = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size': '8'}))
    purchase_order = forms.CharField(required=False)

    class Meta:
        model = Order
        exclude = ('customer', 'state', 'paid', 'distributor')
        
    def __init__(self, order=None, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        #sublist = list(Party.subclass_objects.all().exclude(pk=1))
        #sublist.sort(lambda x, y: cmp(y.__class__, x.__class__))
        #self.fields['distributor'].choices = [(party.id, party.short_name) for party in Party.subclass_objects.all_distributors()]
        #import pdb; pdb.set_trace()
        if order:
            try:
                transportation_tx = TransportationTransaction.objects.get(order=order)
                self.initial['transportation_fee'] = transportation_tx.amount
            except TransportationTransaction.DoesNotExist:
                pass


class OrderItemForm(forms.ModelForm):
     product_id = forms.CharField(widget=forms.HiddenInput)
     producer_id = forms.CharField(widget=forms.HiddenInput)
     avail = forms.DecimalField(widget=forms.TextInput(attrs={
         'readonly':'true', 
         'class': 'read-only-input', 
         'size': '5', 
         'style': 'text-align: right;',
     }))
     quantity = forms.DecimalField(widget=forms.TextInput(attrs={
         'class': 'quantity-field', 
         'size': '5'
     }))
     unit_price = forms.DecimalField(widget=forms.TextInput(attrs={
         'class': 'read-only-input unit-price-field', 
         'size': '5',
         'style': 'text-align: right;',
     }))
     notes = forms.CharField(required=False, widget=forms.TextInput(attrs={
         'size': '32', 
         'value': '',
     }))

     class Meta:
         model = OrderItem
         exclude = ('order', 'product','producer', 'fee')

class MemberPlanSelectionForm(forms.Form):
    plan_from_date = forms.DateField(
        widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    plan_to_date = forms.DateField(
        widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    list_type = forms.ChoiceField( widget=forms.RadioSelect(), choices=[
        ['M','My Product Lists'],['A','All Products']] )


class ProductListForm(forms.ModelForm):

    class Meta:
        model = MemberProductList
        exclude = ('member',)

class CustomerProductForm(forms.ModelForm):
    prod_id = forms.CharField(widget=forms.HiddenInput)
    #default_quantity = forms.DecimalField(required=False, widget=forms.TextInput(attrs={
    #    'class': 'quantity-field', 
    #    'size': '5',
    #    'value': 0,
    #}))
    added = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'added',}))

    class Meta:
        model = CustomerProduct
        exclude = ('customer', 'product', 'product_list', 'default_quantity', 'planned')


class InlineCustomerProductForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InlineCustomerProductForm, self).__init__(*args, **kwargs)
        self.fields['product'].choices = [('', '-------------')] + [
            (prod.id, " ".join([prod.long_name, prod.growing_method])) for prod in Product.objects.filter(sellable=True)]

    
    class Meta:
        model = CustomerProduct
        exclude = ('customer', 'product_list', 'default_quantity', 'planned')




