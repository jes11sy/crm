from rest_framework import serializers
from .models import Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii, Roli, Polzovateli, PhoneGoroda, Zayavki, ZayavkaFile, MasterPayout
from django.contrib.auth.hashers import make_password

class GorodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gorod
        fields = '__all__'

class TipZayavkiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipZayavki
        fields = '__all__'

class RKSerializer(serializers.ModelSerializer):
    class Meta:
        model = RK
        fields = '__all__'

class MasterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    gorod_name = serializers.CharField(source='gorod.name', read_only=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    passport = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Master
        fields = '__all__'
        extra_fields = ['gorod_name']

    def create(self, validated_data):
        raw_password = None
        if 'password' in validated_data:
            raw_password = validated_data['password']
            validated_data['password'] = make_password(validated_data['password'])
        instance = Master(**validated_data)
        instance.save(raw_password=raw_password)
        return instance

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class TipTranzakciiSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipTranzakcii
        fields = '__all__'

class TranzakciiSerializer(serializers.ModelSerializer):
    gorod_name = serializers.CharField(source='gorod.name', read_only=True)
    tip_tranzakcii_name = serializers.CharField(source='tip_tranzakcii.name', read_only=True)
    class Meta:
        model = Tranzakcii
        fields = '__all__'
        extra_fields = ['gorod_name', 'tip_tranzakcii_name']

class RoliSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roli
        fields = '__all__'

class PolzovateliSerializer(serializers.ModelSerializer):
    gorod_name = serializers.CharField(source='gorod.name', read_only=True)
    rol_name = serializers.CharField(source='rol.name', read_only=True)

    class Meta:
        model = Polzovateli
        fields = '__all__'
        extra_fields = ['gorod_name', 'rol_name']

    def create(self, validated_data):
        # Хэшируем пароль
        if 'password' in validated_data:
            raw_password = validated_data['password']
            validated_data['password'] = make_password(raw_password)
            # Если note не передан — заполняем только логин (БЕЗ ПАРОЛЯ!)
            if not validated_data.get('note'):
                login = validated_data.get('login', '')
                validated_data['note'] = f'Логин: {login}'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Хэшируем пароль при обновлении, если он есть
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class PhoneGorodaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneGoroda
        fields = '__all__'

class ZayavkiSerializer(serializers.ModelSerializer):
    rk_name = serializers.CharField(source='rk.rk_name', read_only=True)
    gorod_name = serializers.CharField(source='gorod.name', read_only=True)
    tip_zayavki_name = serializers.CharField(source='tip_zayavki.name', read_only=True)
    master_name = serializers.CharField(source='master.name', read_only=True)
    phone_atc = serializers.CharField(required=False, allow_null=True)
    itog = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    rashod = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    chistymi = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    sdacha_mastera = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    comment_master = serializers.CharField(required=False, allow_null=True)
    comment_kc = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Zayavki
        fields = '__all__'
        extra_fields = ['rk_name', 'gorod_name', 'tip_zayavki_name', 'master_name']

    def update(self, instance, validated_data):
        prev_status = instance.status
        updated_instance = super().update(instance, validated_data)
        # Проверяем условия для создания транзакции
        if (
            validated_data.get('status') == 'Готово' and
            updated_instance.master and
            updated_instance.itog is not None and
            updated_instance.rashod is not None and
            updated_instance.chistymi is not None and
            updated_instance.sdacha_mastera is not None
        ):
            note = f'Приход по Заявке "{updated_instance.id}"'
            if not Tranzakcii.objects.filter(tip_tranzakcii__name='Приход', gorod=updated_instance.gorod, summa=updated_instance.sdacha_mastera).exists():
                try:
                    tip_tr = TipTranzakcii.objects.get(name='Приход')
                    Tranzakcii.objects.create(
                        gorod=updated_instance.gorod,
                        tip_tranzakcii=tip_tr,
                        summa=updated_instance.sdacha_mastera,
                        note=note
                    )
                except TipTranzakcii.DoesNotExist:
                    pass
        return updated_instance

class ZayavkaFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    file = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = ZayavkaFile
        fields = ['id', 'zayavka', 'file', 'type', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']

class MasterPayoutSerializer(serializers.ModelSerializer):
    zayavka = serializers.PrimaryKeyRelatedField(queryset=Zayavki.objects.all())
    zayavka_id = serializers.IntegerField(source='zayavka.id', read_only=True)
    zayavka_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MasterPayout
        fields = ['id', 'zayavka', 'zayavka_id', 'zayavka_info', 'summa', 'status', 'comment', 'file', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'zayavka_id', 'zayavka_info']

    def get_zayavka_info(self, obj):
        if not obj.zayavka:
            return None
        return {
            'id': obj.zayavka.id,
            'master_name': obj.zayavka.master.name if obj.zayavka.master else None,
            'gorod_name': obj.zayavka.gorod.name if obj.zayavka.gorod else None,
        } 