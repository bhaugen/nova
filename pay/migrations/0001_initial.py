# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PayPalSettings'
        db.create_table('pay_paypalsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('business', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('use_sandbox', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pay', ['PayPalSettings'])


    def backwards(self, orm):
        
        # Deleting model 'PayPalSettings'
        db.delete_table('pay_paypalsettings')


    models = {
        'pay.paypalsettings': {
            'Meta': {'object_name': 'PayPalSettings'},
            'business': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'use_sandbox': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['pay']
