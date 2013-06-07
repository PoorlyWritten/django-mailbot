# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TemplatedEmailMessage'
        db.create_table('email_integration_templatedemailmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('text_content', self.gf('django.db.models.fields.TextField')()),
            ('html_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('email_integration', ['TemplatedEmailMessage'])

        # Adding model 'EmailProfile'
        db.create_table('email_integration_emailprofile', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('email_integration', ['EmailProfile'])

        # Adding model 'RawEmail'
        db.create_table('email_integration_rawemail', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_parsed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('parsed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parsed_emails', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('email_integration', ['RawEmail'])

        # Adding model 'EmailAddress'
        db.create_table('email_integration_emailaddress', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email_integration.EmailProfile'], null=True, blank=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('address_hash', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True)),
            ('verification_hash', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('verification_email_sent', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('verification_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('email_integration', ['EmailAddress'])


    def backwards(self, orm):
        # Deleting model 'TemplatedEmailMessage'
        db.delete_table('email_integration_templatedemailmessage')

        # Deleting model 'EmailProfile'
        db.delete_table('email_integration_emailprofile')

        # Deleting model 'RawEmail'
        db.delete_table('email_integration_rawemail')

        # Deleting model 'EmailAddress'
        db.delete_table('email_integration_emailaddress')


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
        'email_integration.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'address_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email_integration.EmailProfile']", 'null': 'True', 'blank': 'True'}),
            'verification_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verification_email_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'verification_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'email_integration.emailprofile': {
            'Meta': {'object_name': 'EmailProfile'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'email_integration.rawemail': {
            'Meta': {'object_name': 'RawEmail'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_parsed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'parsed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parsed_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'email_integration.templatedemailmessage': {
            'Meta': {'object_name': 'TemplatedEmailMessage'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'html_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'text_content': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['email_integration']