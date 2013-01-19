# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FollowUp'
        db.create_table('introductions_followup', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=128, null=True)),
            ('other_email', self.gf('django.db.models.fields.EmailField')(max_length=128, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('introduction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['introductions.Introduction'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('custom_url', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True, null=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('requested', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('rating_votes', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('rating_score', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('introductions', ['FollowUp'])

        # Adding unique constraint on 'FollowUp', fields ['introduction', 'email']
        db.create_unique('introductions_followup', ['introduction_id', 'email'])

        # Adding model 'Introduction'
        db.create_table('introductions_introduction', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('connector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('introducee1', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('introducee2', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('email_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['email_integration.RawEmail'], unique=True, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('introductions', ['Introduction'])


    def backwards(self, orm):
        # Removing unique constraint on 'FollowUp', fields ['introduction', 'email']
        db.delete_unique('introductions_followup', ['introduction_id', 'email'])

        # Deleting model 'FollowUp'
        db.delete_table('introductions_followup')

        # Deleting model 'Introduction'
        db.delete_table('introductions_introduction')


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
        'email_integration.rawemail': {
            'Meta': {'object_name': 'RawEmail'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_parsed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'parsed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parsed_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'introductions.followup': {
            'Meta': {'unique_together': "(('introduction', 'email'),)", 'object_name': 'FollowUp'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_url': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '128', 'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['introductions.Introduction']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'other_email': ('django.db.models.fields.EmailField', [], {'max_length': '128', 'null': 'True'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'requested': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'introductions.introduction': {
            'Meta': {'object_name': 'Introduction'},
            'connector': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['email_integration.RawEmail']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'introducee1': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'introducee2': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['introductions']