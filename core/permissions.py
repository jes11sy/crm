from rest_framework import permissions

class IsDirectorOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только директорам и администраторам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role in ['director', 'admin']

class IsCallCentreOrAbove(permissions.BasePermission):
    """
    Разрешает доступ call-центру и выше (мастера, директоры, администраторы).
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role in ['callcentre', 'kc', 'avitolog', 'master', 'director', 'admin']

class IsMasterOrAbove(permissions.BasePermission):
    """
    Разрешает доступ мастерам, директорам и администраторам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role in ['master', 'director', 'admin']

class IsKCUserOrAbove(permissions.BasePermission):
    """
    Разрешает доступ КЦ пользователям, мастерам, директорам и администраторам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role in ['kc', 'callcentre', 'avitolog', 'master', 'director', 'admin']

class IsSameCity(permissions.BasePermission):
    """
    Разрешает доступ к объектам только из того же города.
    Администраторы имеют доступ ко всем городам.
    Директоры имеют доступ только к своему городу.
    Остальные пользователи имеют доступ только к своему городу.
    """
    def has_permission(self, request, view):
        # Разрешаем всем аутентифицированным пользователям
        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True
        # Для директора проверяем, что объект принадлежит его городу
        if hasattr(request.user, 'role') and request.user.role == 'director':
            if hasattr(obj, 'gorod') and hasattr(request.user, 'gorod'):
                return obj.gorod == request.user.gorod
            elif hasattr(obj, 'gorod_id') and hasattr(request.user, 'gorod'):
                return obj.gorod_id == request.user.gorod.id
            return False
        # Для остальных ролей проверяем, что объект принадлежит тому же городу
        if hasattr(obj, 'gorod') and hasattr(request.user, 'gorod'):
            return obj.gorod == request.user.gorod
        elif hasattr(obj, 'gorod_id') and hasattr(request.user, 'gorod'):
            return obj.gorod_id == request.user.gorod.id
        return False

class IsOwnerOrSameCity(permissions.BasePermission):
    """
    Разрешает доступ владельцу объекта или пользователям из того же города.
    Администраторы имеют доступ ко всем объектам.
    Директоры имеют доступ только к объектам своего города.
    """
    def has_permission(self, request, view):
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True
        return True
    
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True
        # Проверяем, является ли пользователь владельцем
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        # Для директора проверяем, что объект принадлежит его городу
        if hasattr(request.user, 'role') and request.user.role == 'director':
            if hasattr(obj, 'gorod') and hasattr(request.user, 'gorod'):
                return obj.gorod == request.user.gorod
            elif hasattr(obj, 'gorod_id') and hasattr(request.user, 'gorod'):
                return obj.gorod_id == request.user.gorod.id
            return False
        # Для остальных ролей проверяем, что объект принадлежит тому же городу
        if hasattr(obj, 'gorod') and hasattr(request.user, 'gorod'):
            return obj.gorod == request.user.gorod
        elif hasattr(obj, 'gorod_id') and hasattr(request.user, 'gorod'):
            return obj.gorod_id == request.user.gorod.id
        return False

class IsReadOnlyForKC(permissions.BasePermission):
    """
    Разрешает только чтение для КЦ пользователей.
    Мастера, директоры и администраторы имеют полный доступ.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        if request.user.role in ['master', 'director', 'admin']:
            return True
        elif request.user.role in ['kc', 'avitolog']:
            return request.method in permissions.SAFE_METHODS
        return False

class IsMasterOrDirectorForMasterData(permissions.BasePermission):
    """
    Разрешает доступ к данным мастеров только мастерам и директорам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role in ['master', 'director', 'admin']

class IsAdminOnly(permissions.BasePermission):
    """
    Разрешает доступ только администраторам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role == 'admin'

class IsDirectorOrAdminForFinancial(permissions.BasePermission):
    """
    Разрешает доступ к финансовым данным только директорам и администраторам.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'role'):
            return False
        return request.user.role == 'admin' 