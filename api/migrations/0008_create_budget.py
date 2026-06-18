from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_transfer_spending_do_nothing'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(
                    choices=[
                        ('active', 'Active'),
                        ('closed', 'Closed'),
                        ('draft', 'Draft'),
                    ],
                    default='active',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='budgets',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('family', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='budgets',
                    to='api.family',
                )),
            ],
            options={
                'db_table': 'budgets',
                'constraints': [
                    models.CheckConstraint(
                        check=(
                            models.Q(user__isnull=False) |
                            models.Q(family__isnull=False)
                        ),
                        name='budgets_owner_check',
                    ),
                ],
            },
        ),
    ]
