from .models import PostViewCount
from .utilities import get_client_ip

class PostViewCountMixin:
    '''Миксин, увеличивающий просмотры'''
    def get_object(self):
        obj = super().get_object()
        ip_address = get_client_ip(self.request)
        if hasattr(self.request, 'user'):
            user = self.request.user
            PostViewCount.objects.get_or_create(post=obj,
                                        ip_address=ip_address,
                                        user=user)
        else:
            PostViewCount.objects.get_or_create(post=obj,
                                        ip_address=ip_address)