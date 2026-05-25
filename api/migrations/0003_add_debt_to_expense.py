from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_currency_to_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='debt',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='linked_expenses',
                to='api.debt',
            ),
        ),
    ]
