# Generated by Django 5.2.4 on 2025-07-18 20:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
        ('content', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('assessment_type', models.CharField(choices=[('phq9', 'PHQ-9 (Depression)'), ('gad7', 'GAD-7 (Anxiety)'), ('pcl5', 'PCL-5 (PTSD)'), ('custom', 'Custom Assessment')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('version', models.CharField(default='1.0', max_length=10)),
                ('min_score', models.IntegerField(default=0)),
                ('max_score', models.IntegerField(default=27)),
            ],
        ),
        migrations.RemoveField(
            model_name='assessmentresult',
            name='form',
        ),
        migrations.RemoveField(
            model_name='assessmentresult',
            name='user',
        ),
        migrations.CreateModel(
            name='AssessmentResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('risk_level', models.CharField(choices=[('none', 'None/Minimal'), ('mild', 'Mild'), ('moderate', 'Moderate'), ('moderately_severe', 'Moderately Severe'), ('severe', 'Severe')], max_length=20)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('is_flagged', models.BooleanField(default=False)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.assessment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-completed_at'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('question_type', models.CharField(choices=[('likert', 'Likert Scale'), ('multiple', 'Multiple Choice'), ('text', 'Text Response')], default='likert', max_length=20)),
                ('order', models.PositiveIntegerField(default=0)),
                ('weight', models.FloatField(default=1.0)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='assessments.assessment')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='LikertOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('value', models.IntegerField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='assessments.question')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_score', models.IntegerField()),
                ('max_score', models.IntegerField()),
                ('risk_level', models.CharField(choices=[('none', 'None/Minimal'), ('mild', 'Mild'), ('moderate', 'Moderate'), ('moderately_severe', 'Moderately Severe'), ('severe', 'Severe')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('action_items', models.TextField(help_text='Bullet-point list of actions')),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='assessments.assessment')),
                ('resources', models.ManyToManyField(blank=True, to='content.educationalcontent')),
            ],
            options={
                'ordering': ['assessment', 'min_score'],
            },
        ),
        migrations.CreateModel(
            name='ResponseAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_value', models.IntegerField(blank=True, null=True)),
                ('answer_text', models.TextField(blank=True, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.question')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='assessments.assessmentresponse')),
            ],
        ),
        migrations.DeleteModel(
            name='AssessmentForm',
        ),
        migrations.DeleteModel(
            name='AssessmentResult',
        ),
    ]
