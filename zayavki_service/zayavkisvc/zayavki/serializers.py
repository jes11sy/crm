from rest_framework import serializers
from .models import TipZayavki, Zayavka, ZayavkaFile

class TipZayavkiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipZayavki
        fields = '__all__'

class ZayavkaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZayavkaFile
        fields = '__all__'

class ZayavkaSerializer(serializers.ModelSerializer):
    files = ZayavkaFileSerializer(many=True, read_only=True)
    tip = TipZayavkiSerializer(read_only=True)
    tip_id = serializers.PrimaryKeyRelatedField(queryset=TipZayavki.objects.all(), source='tip', write_only=True)

    class Meta:
        model = Zayavka
        fields = '__all__'

    def validate(self, data):
        if not data.get('user_id'):
            raise serializers.ValidationError({'user_id': 'user_id обязателен'})
        if not data.get('tip') and not data.get('tip_id'):
            raise serializers.ValidationError({'tip_id': 'tip_id обязателен'})
        allowed_statuses = ['new', 'in_progress', 'done', 'cancelled']
        status_val = data.get('status') or getattr(self.instance, 'status', None)
        if status_val and status_val not in allowed_statuses:
            raise serializers.ValidationError({'status': f'Недопустимый статус: {status_val}'})
        return data 