# Generated by Django 2.2.7 on 2019-12-06 00:17

from django.db import migrations, models
import django_logic.process


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('draft', 'Draft'), ('paid', 'Paid'), ('void', 'Void')], default='draft', max_length=16, null=True)),
                ('customer_received', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=True)),
            ],
            bases=(django_logic.process.Process, models.Model),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.CharField(blank=True, max_length=16)),
            ],
        ),
    ]
