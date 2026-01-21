from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tlog', '0020_add_my_callsign_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(help_text='Имя пользователя (callsign)', max_length=150)),
                ('message', models.TextField(help_text='Текст сообщения')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='chat_messages', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]