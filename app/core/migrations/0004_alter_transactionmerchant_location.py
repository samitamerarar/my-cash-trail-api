# Generated by Django 4.2.2 on 2023-07-02 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_transactionmerchant_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionmerchant',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]