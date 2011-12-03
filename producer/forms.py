from django import forms
from django.db.models.query import QuerySet

import datetime

from distribution.models import *

class ProducerProfileForm(forms.ModelForm):
    long_name = forms.CharField(widget=forms.TextInput(attrs={'size': '50', 'value': ''}))
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


    class Meta:
        model = Producer
        exclude = ('member_id', 'short_name', 'delivers')


class ProducerContactForm(forms.ModelForm): 
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '16', 'value': ''}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    cell = forms.CharField(widget=forms.TextInput(attrs={'size': '10', 'value': ''}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size': '32', 'value': ''}))

    class Meta:
        model = ProducerContact
        exclude = ('login_user', 'cell')


class InventoryItemForm(forms.ModelForm):
    prod_id = forms.CharField(widget=forms.HiddenInput)
    freeform_lot_id = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'size': '16', 'value': ''}))
    field_id = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'size': '5', 'value': ''}))
    inventory_date = forms.DateField(widget=forms.TextInput(attrs={'size': '10'}))
    planned = forms.DecimalField(widget=forms.TextInput(attrs={'class':
                                                               'quantity-field',
                                                               'size': '6'}))
    notes = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '32', 'value': ''}))
    item_id = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = InventoryItem
        exclude = ('producer', 'product', 'received', 'onhand', 'remaining', 'expiration_date')
        
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

