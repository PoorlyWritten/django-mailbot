# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailWhitelist'
        db.create_table(u'email_integration_emailwhitelist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_address', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('activated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'email_integration', ['EmailWhitelist'])


        # Changing field 'EmailProfile.user'
        db.alter_column(u'email_integration_emailprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True))
        # Adding unique constraint on 'EmailProfile', fields ['user']
        db.create_unique(u'email_integration_emailprofile', ['user_id'])

        # Adding M2M table for field email_addresses on 'RawEmail'
        db.create_table(u'email_integration_rawemail_email_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rawemail', models.ForeignKey(orm[u'email_integration.rawemail'], null=False)),
            ('emailaddress', models.ForeignKey(orm[u'email_integration.emailaddress'], null=False))
        ))
        db.create_unique(u'email_integration_rawemail_email_addresses', ['rawemail_id', 'emailaddress_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'EmailProfile', fields ['user']
        db.delete_unique(u'email_integration_emailprofile', ['user_id'])

        # Deleting model 'EmailWhitelist'
        db.delete_table(u'email_integration_emailwhitelist')


        # Changing field 'EmailProfile.user'
        db.alter_column(u'email_integration_emailprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))
        # Removing M2M table for field email_addresses on 'RawEmail'
        db.delete_table('email_integration_rawemail_email_addresses')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'email_integration.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'address_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['email_integration.EmailProfile']", 'null': 'True', 'blank': 'True'}),
            'verification_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verification_email_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'verification_hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'email_integration.emailprofile': {
            'Meta': {'object_name': 'EmailProfile'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_approved': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'email_integration.emailwhitelist': {
            'Meta': {'object_name': 'EmailWhitelist'},
            'activated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'email_address': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'email_integration.rawemail': {
            'Meta': {'object_name': 'RawEmail'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_parsed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['email_integration.EmailAddress']", 'null': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'parsed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parsed_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'email_integration.templatedemailmessage': {
            'Meta': {'object_name': 'TemplatedEmailMessage'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'html_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'text_content': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['email_integration']