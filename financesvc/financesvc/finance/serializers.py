from rest_framework import serializers
from .models import TipTranzakcii, Tranzakciya, Payout

class TipTranzakciiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipTranzakcii
        fields = '__all__'

class TranzakciyaSerializer(serializers.ModelSerializer):
    tip = TipTranzakciiSerializer(read_only=True)
    tip_id = serializers.PrimaryKeyRelatedField(queryset=TipTranzakcii.objects.all(), source='tip', write_only=True)

    class Meta:
        model = Tranzakciya
        fields = '__all__'

    def validate(self, data):
        if not data.get('user_id'):
            raise serializers.ValidationError({'user_id': 'user_id обязателен'})
        if not data.get('tip') and not data.get('tip_id'):
            raise serializers.ValidationError({'tip_id': 'tip_id обязателен'})
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Сумма должна быть больше нуля'})
        allowed_statuses = ['pending', 'completed', 'failed', 'cancelled']
        status_val = data.get('status') or getattr(self.instance, 'status', None)
        if status_val and status_val not in allowed_statuses:
            raise serializers.ValidationError({'status': f'Недопустимый статус: {status_val}'})
        return data

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = '__all__'

    def validate(self, data):
        if not data.get('master_id'):
            raise serializers.ValidationError({'master_id': 'master_id обязателен'})
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Сумма должна быть больше нуля'})
        allowed_statuses = ['pending', 'completed', 'failed', 'cancelled']
        status_val = data.get('status') or getattr(self.instance, 'status', None)
        if status_val and status_val not in allowed_statuses:
            raise serializers.ValidationError({'status': f'Недопустимый статус: {status_val}'})
        allowed_methods = ['bank', 'card', 'cash']
        method_val = data.get('payment_method') or getattr(self.instance, 'payment_method', None)
        if method_val and method_val not in allowed_methods:
            raise serializers.ValidationError({'payment_method': f'Недопустимый способ выплаты: {method_val}'})
        return data 