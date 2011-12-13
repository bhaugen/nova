# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'InventoryItem.unit_price'
        db.add_column('distribution_inventoryitem', 'unit_price', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=8, decimal_places=2), keep_default=False)

        # Changing field 'ProducerProduct.price_change_delivery_date'
        db.alter_column('distribution_producerproduct', 'price_change_delivery_date', self.gf('django.db.models.fields.DateField')())


    def backwards(self, orm):
        
        # Deleting field 'InventoryItem.unit_price'
        db.delete_column('distribution_inventoryitem', 'unit_price')

        # Changing field 'ProducerProduct.price_change_delivery_date'
        db.alter_column('distribution_producerproduct', 'price_change_delivery_date', self.gf('django.db.models.fields.DateField')(null=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'distribution.customer': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Customer', '_ormbases': ['distribution.Party']},
            'apply_transportation_fee': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'customer_transportation_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'party_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.Party']", 'unique': 'True', 'primary_key': 'True'})
        },
        'distribution.customercontact': {
            'Meta': {'object_name': 'CustomerContact'},
            'cell': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['distribution.Customer']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '96', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'customer_contact'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'})
        },
        'distribution.customerdeliverycycle': {
            'Meta': {'unique_together': "(('customer', 'delivery_cycle'),)", 'object_name': 'CustomerDeliveryCycle'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delivery_cycles'", 'to': "orm['distribution.Customer']"}),
            'delivery_cycle': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delivery_customers'", 'to': "orm['distribution.DeliveryCycle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'distribution.customerpayment': {
            'Meta': {'object_name': 'CustomerPayment'},
            'amount_paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customer_payments'", 'to': "orm['distribution.Order']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paid_orders'", 'to': "orm['distribution.Payment']"})
        },
        'distribution.customerproduct': {
            'Meta': {'ordering': "('customer', 'product')", 'unique_together': "(('customer', 'product', 'product_list'),)", 'object_name': 'CustomerProduct'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customer_products'", 'to': "orm['distribution.Party']"}),
            'default_quantity': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planned': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Product']"}),
            'product_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.MemberProductList']", 'null': 'True', 'blank': 'True'})
        },
        'distribution.deliverycycle': {
            'Meta': {'ordering': "('delivery_day',)", 'object_name': 'DeliveryCycle'},
            'customers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['distribution.Customer']", 'through': "orm['distribution.CustomerDeliveryCycle']", 'symmetrical': 'False'}),
            'delivery_day': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': "'1'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory_closing_day': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'max_length': "'1'"}),
            'inventory_closing_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(12, 0)'}),
            'order_closing_day': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': "'1'"}),
            'order_closing_time': ('django.db.models.fields.TimeField', [], {}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'distribution.distributor': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Distributor', '_ormbases': ['distribution.Party']},
            'party_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.Party']", 'unique': 'True', 'primary_key': 'True'}),
            'transportation_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'})
        },
        'distribution.economicevent': {
            'Meta': {'object_name': 'EconomicEvent'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'from_whom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'given_events'", 'to': "orm['distribution.Party']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'to_whom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taken_events'", 'to': "orm['distribution.Party']"}),
            'transaction_date': ('django.db.models.fields.DateField', [], {})
        },
        'distribution.emailintro': {
            'Meta': {'object_name': 'EmailIntro'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notice_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_intro'", 'to': "orm['notification.NoticeType']"})
        },
        'distribution.foodnetwork': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'FoodNetwork', '_ormbases': ['distribution.Party']},
            'customer_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '4', 'decimal_places': '2'}),
            'customer_fee_label': ('django.db.models.fields.CharField', [], {'default': "'Delivery Cost'", 'max_length': '64'}),
            'customer_terms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'default_product_expiration_days': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'member_terms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'next_delivery_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'order_by_lot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'party_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.Party']", 'unique': 'True', 'primary_key': 'True'}),
            'producer_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '4', 'decimal_places': '2'}),
            'producer_fee_label': ('django.db.models.fields.CharField', [], {'default': "'Marketing Cost'", 'max_length': '64'}),
            'transportation_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'use_plans_for_ordering': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'distribution.inventoryitem': {
            'Meta': {'ordering': "('product', 'producer', 'inventory_date')", 'object_name': 'InventoryItem'},
            'custodian': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'custody_items'", 'null': 'True', 'to': "orm['distribution.Party']"}),
            'expiration_date': ('django.db.models.fields.DateField', [], {}),
            'field_id': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'freeform_lot_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory_date': ('django.db.models.fields.DateField', [], {}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'onhand': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'planned': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inventory_items'", 'to': "orm['distribution.Party']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Product']"}),
            'received': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'remaining': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'})
        },
        'distribution.inventorytransaction': {
            'Meta': {'ordering': "('-transaction_date',)", 'object_name': 'InventoryTransaction', '_ormbases': ['distribution.EconomicEvent']},
            'economicevent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.EconomicEvent']", 'unique': 'True', 'primary_key': 'True'}),
            'inventory_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.InventoryItem']"}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.OrderItem']", 'null': 'True', 'blank': 'True'}),
            'process': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'inventory_transactions'", 'null': 'True', 'to': "orm['distribution.Process']"}),
            'transaction_type': ('django.db.models.fields.CharField', [], {'default': "'Delivery'", 'max_length': '10'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'distribution.memberproductlist': {
            'Meta': {'object_name': 'MemberProductList'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product_lists'", 'to': "orm['distribution.Party']"})
        },
        'distribution.order': {
            'Meta': {'ordering': "('order_date', 'customer')", 'object_name': 'Order'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_changed'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders_created'", 'null': 'True', 'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Customer']"}),
            'delivery_date': ('django.db.models.fields.DateField', [], {}),
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders'", 'null': 'True', 'to': "orm['distribution.Party']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_date': ('django.db.models.fields.DateField', [], {}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product_list': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders'", 'null': 'True', 'to': "orm['distribution.MemberProductList']"}),
            'purchase_order': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'Submitted'", 'max_length': '16', 'blank': 'True'})
        },
        'distribution.orderitem': {
            'Meta': {'ordering': "('order', 'product')", 'object_name': 'OrderItem'},
            'fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '4', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Order']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'})
        },
        'distribution.orderitemchange': {
            'Meta': {'object_name': 'OrderItemChange'},
            'action': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': "'1'"}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_items_changed'", 'null': 'True', 'to': "orm['auth.User']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_changes'", 'to': "orm['distribution.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_notes': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'new_qty': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_changes'", 'null': 'True', 'to': "orm['distribution.Order']"}),
            'order_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_item_changes'", 'null': 'True', 'to': "orm['distribution.OrderItem']"}),
            'prev_notes': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'prev_qty': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_item_changes'", 'to': "orm['distribution.Product']"}),
            'reason': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': "'1'"}),
            'when_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'distribution.party': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Party'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '96', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'member_id': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'storage_capacity': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'distribution.partyuser': {
            'Meta': {'object_name': 'PartyUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'to': "orm['distribution.Party']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parties'", 'to': "orm['auth.User']"})
        },
        'distribution.payment': {
            'Meta': {'ordering': "('transaction_date',)", 'object_name': 'Payment', '_ormbases': ['distribution.EconomicEvent']},
            'economicevent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.EconomicEvent']", 'unique': 'True', 'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        'distribution.process': {
            'Meta': {'ordering': "('process_date',)", 'object_name': 'Process'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'managed_processes'", 'null': 'True', 'to': "orm['distribution.Party']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'process_date': ('django.db.models.fields.DateField', [], {}),
            'process_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.ProcessType']"})
        },
        'distribution.processor': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Processor', '_ormbases': ['distribution.Party']},
            'party_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.Party']", 'unique': 'True', 'primary_key': 'True'})
        },
        'distribution.processtype': {
            'Meta': {'object_name': 'ProcessType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'input_types'", 'to': "orm['distribution.Product']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number_of_output_lots': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'number_of_processing_steps': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'output_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'output_types'", 'to': "orm['distribution.Product']"}),
            'use_existing_input_lot': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'distribution.producer': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Producer', '_ormbases': ['distribution.Party']},
            'delivers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'party_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.Party']", 'unique': 'True', 'primary_key': 'True'}),
            'philosophy': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'producer_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '4', 'decimal_places': '2'})
        },
        'distribution.producercontact': {
            'Meta': {'object_name': 'ProducerContact'},
            'cell': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '96', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'producer_contact'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['distribution.Producer']"})
        },
        'distribution.producerpricechange': {
            'Meta': {'ordering': "('-when_changed',)", 'object_name': 'ProducerPriceChange'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'producer_prices_changed'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price_change_delivery_date': ('django.db.models.fields.DateField', [], {}),
            'producer_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'producer_product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'price_changes'", 'to': "orm['distribution.ProducerProduct']"}),
            'when_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'distribution.producerproduct': {
            'Meta': {'ordering': "('producer', 'product')", 'unique_together': "(('producer', 'product'),)", 'object_name': 'ProducerProduct'},
            'default_avail_qty': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'producer_distributors'", 'null': 'True', 'to': "orm['distribution.Party']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'planned': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'price_change_delivery_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'price_changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'producer_products_changed'", 'null': 'True', 'to': "orm['auth.User']"}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'producer_products'", 'to': "orm['distribution.Party']"}),
            'producer_fee': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '4', 'decimal_places': '2'}),
            'producer_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product_producers'", 'to': "orm['distribution.Product']"}),
            'qty_per_year': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'})
        },
        'distribution.product': {
            'Meta': {'ordering': "('short_name',)", 'object_name': 'Product'},
            'customer_fee_override': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '2', 'blank': 'True'}),
            'expiration_days': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'growing_method': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_parent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['distribution.Product']"}),
            'pay_producer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'pay_producer_on_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'plannable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'producer_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'producer_price_maximum': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'producer_price_minimum': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'sellable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'stockable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'distribution.productplan': {
            'Meta': {'ordering': "('product', 'member', 'from_date')", 'object_name': 'ProductPlan'},
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'plan_distributors'", 'null': 'True', 'to': "orm['distribution.Party']"}),
            'from_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product_plans'", 'to': "orm['distribution.Party']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'producer'", 'max_length': '12'}),
            'to_date': ('django.db.models.fields.DateField', [], {})
        },
        'distribution.servicetransaction': {
            'Meta': {'object_name': 'ServiceTransaction', '_ormbases': ['distribution.EconomicEvent']},
            'economicevent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.EconomicEvent']", 'unique': 'True', 'primary_key': 'True'}),
            'process': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'service_transactions'", 'to': "orm['distribution.Process']"}),
            'service_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.ServiceType']"})
        },
        'distribution.servicetype': {
            'Meta': {'object_name': 'ServiceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoiced_separately': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'pay_provider_on_terms': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'distribution.special': {
            'Meta': {'ordering': "('-from_date',)", 'object_name': 'Special'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'from_date': ('django.db.models.fields.DateField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '8', 'decimal_places': '2'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'specials'", 'to': "orm['distribution.Product']"}),
            'to_date': ('django.db.models.fields.DateField', [], {})
        },
        'distribution.staffcontact': {
            'Meta': {'object_name': 'StaffContact'},
            'cell': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '96', 'null': 'True', 'blank': 'True'}),
            'food_network': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contacts'", 'to': "orm['distribution.FoodNetwork']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'staff_contact'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'role': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4', 'max_length': "'1'"})
        },
        'distribution.transactionpayment': {
            'Meta': {'object_name': 'TransactionPayment'},
            'amount_paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid_event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transaction_payments'", 'to': "orm['distribution.EconomicEvent']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'paid_events'", 'to': "orm['distribution.Payment']"})
        },
        'distribution.transportationtransaction': {
            'Meta': {'object_name': 'TransportationTransaction', '_ormbases': ['distribution.EconomicEvent']},
            'economicevent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['distribution.EconomicEvent']", 'unique': 'True', 'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.Order']"}),
            'service_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['distribution.ServiceType']"})
        },
        'notification.noticetype': {
            'Meta': {'object_name': 'NoticeType'},
            'default': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'display': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['distribution']
