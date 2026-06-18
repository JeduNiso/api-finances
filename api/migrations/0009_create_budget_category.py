from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_create_budget'),
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('budget', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='budget_categories',
                    to='api.budget',
                )),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.RESTRICT,
                    related_name='budget_categories',
                    to='api.category',
                )),
            ],
            options={
                'db_table': 'budget_categories',
                'unique_together': {('budget', 'category')},
            },
        ),
    ]
