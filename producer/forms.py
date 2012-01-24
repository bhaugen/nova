from django import forms
from django.db.models.query import QuerySet
from django.forms.util import ErrorList
from django.conf import settings

import datetime

from distribution.models import *


class TdErrorList(ErrorList):
    def __unicode__(self):
        return self.as_tds()
    
    def as_divs(self):
        if not self:
            return u''
        return u'<td class="errorlist">%s</td>' % ''.join([u'<div class="error">%s</div>' % e for e in self])


class ProducerProfileForm(forms.ModelForm):
    long_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
    tag_line = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
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
    specialties = forms.ModelMultipleChoiceField(
        queryset=Specialty.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    philosophy = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    storage_capacity = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols': '60', 'value': ''}))
    background_color = forms.ChoiceField(choices=settings.COLOR_CHOICES)


    class Meta:
        model = Producer
        exclude = ('member_id', 'short_name', 'delivers', 'producer_fee')


class ProducerContactForm(forms.ModelForm): 
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '16', 'value': ''}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    #cell = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '32', 'value': ''}))

    class Meta:
        model = ProducerContact
        exclude = ('login_user', 'cell')


class ProducerProductEditForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    id = forms.CharField(widget=forms.HiddenInput)
    product_id = forms.CharField(widget=forms.HiddenInput)
    producer_price = forms.DecimalField(widget=forms.TextInput(attrs={'class':
                                                               'producer-price',
                                                               'size': '6'}))
    qty_per_year = forms.DecimalField(widget=forms.TextInput(attrs={'class':
                                                               'quantity-field',
                                                               'size': '6'}))
    delete = forms.BooleanField(required=False)

    class Meta:
        model = ProducerProduct
        fields = ('id', 'producer_price', 'qty_per_year',)


class ProducerProductAddForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    product = forms.ModelChoiceField(required=False,
        queryset=QuerySet(model=Product),
        widget=forms.Select(attrs={'class': 'added_product',}))
    producer_price = forms.DecimalField(required=False, widget=forms.TextInput(attrs={
        'class':'added-producer-price', 'size': '6'}))
    qty_per_year = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class':
                                                               'quantity-field',
                                                               'size': '6'}))
    min = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'readonly':'true', 
                                      'class': 'read-only-input', 
                                      'size': '6',
                                      'style': 'text-align: right',
                                     }))
    max = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'readonly':'true', 
                                      'class': 'read-only-input', 
                                      'size': '6',
                                      'style': 'text-align: right',
                                     }))

    def __init__(self, products, *args, **kwargs):
        super(ProducerProductAddForm, self).__init__(*args, **kwargs)
        self.fields['product'].choices = [('', '----------')] + [
            (p.id, p.name_with_method()) for p in products]


    def clean(self):
        cleaned_data = self.cleaned_data
        if self.errors:
            return cleaned_data
        product = cleaned_data.get("product")
        if product:
            producer_price = cleaned_data.get("producer_price")
            min = product.producer_price_minimum
            max = product.producer_price_maximum

            msg = None
            if min:
                if producer_price < min:
                    msg = u" ".join(["Set price is less than minimum of", str(min)])
            if max:
                if producer_price > max:
                    msg = u" ".join(["Set price is more than maximum of", str(max)])
            if msg:
                #self._errors["producer_price"] = self.error_class([msg])
                del cleaned_data["producer_price"]
                raise forms.ValidationError(msg)
        return cleaned_data


class InventoryItemForm(forms.ModelForm):
    prod_id = forms.CharField(widget=forms.HiddenInput)
    freeform_lot_id = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'size': '16', 'value': ''}))
    field_id = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'size': '5', 'value': ''}))
    inventory_date = forms.DateField(widget=forms.TextInput(attrs={'size': '10'}))
    expiration_date = forms.DateField(widget=forms.TextInput(attrs={'size': '10'}))
    remaining = forms.DecimalField(widget=forms.TextInput(attrs={'class':
                                                               'quantity-field',
                                                               'size': '6'}))
    notes = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '32', 'value': ''}))
    item_id = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = InventoryItem
        exclude = ('producer', 'product', 'planned', 'received', 'onhand',
                   'unit_price')
        
    def __init__(self, *args, **kwargs):
        super(InventoryItemForm, self).__init__(*args, **kwargs)
        self.fields['custodian'].choices = [('', '------------')] + [(prod.id, prod.short_name) for prod in Party.subclass_objects.possible_custodians()]


class ProcessSelectionForm(forms.Form):
    process_date = forms.DateField(
        widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    process_type = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ProcessSelectionForm, self).__init__(*args, **kwargs)
        self.fields['process_type'].choices = [('', '----------')] + [(pt.id, pt.name) for pt in ProcessType.objects.all()]


class PlanSelectionForm(forms.Form):
    plan_from_date = forms.DateField(
        widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    plan_to_date = forms.DateField(
        widget=forms.TextInput(attrs={"dojoType": "dijit.form.DateTextBox", "constraints": "{datePattern:'yyyy-MM-dd'}"}))
    list_type = forms.ChoiceField( widget=forms.RadioSelect(), choices=[
        ['M','My Planned Products'],['A','All Products']] )


class ProcessServiceForm(forms.ModelForm):
    amount = forms.DecimalField(widget=forms.TextInput(attrs={'class': 'quantity-field', 'size': '10'}))
    
    def __init__(self, *args, **kwargs):
        super(ProcessServiceForm, self).__init__(*args, **kwargs)
        self.fields['from_whom'].choices = [('', '----------')] + [
            (proc.id, proc.short_name) for proc in Party.subclass_objects.producers_and_processors()]

    class Meta:
        model = ServiceTransaction
        exclude = ('process', 'to_whom', 'transaction_date', 'payment', 'notes')

