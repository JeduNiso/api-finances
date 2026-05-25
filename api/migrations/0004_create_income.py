from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_debt_to_expense'),
    ]

    operations = [
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('description', models.CharField(max_length=255)),
                ('received_at', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='incomes', to='api.account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='incomes', to='api.user')),
            ],
            options={
                'db_table': 'incomes',
            },
        ),
    ]
