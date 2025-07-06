from django.contrib import admin
from .models import (
    Gorod, TipZayavki, RK, Master, TipTranzakcii, Tranzakcii, Roli, Polzovateli, PhoneGoroda, Zayavki, MasterPayout
)

admin.site.register(Gorod)
admin.site.register(TipZayavki)
admin.site.register(RK)
admin.site.register(Master)
admin.site.register(TipTranzakcii)
admin.site.register(Tranzakcii)
admin.site.register(Roli)
admin.site.register(Polzovateli)
admin.site.register(PhoneGoroda)
admin.site.register(Zayavki)
admin.site.register(MasterPayout)
