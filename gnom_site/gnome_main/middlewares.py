from .models import SuperPostComment, SubPostComment


class CommentsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if len(request.get_full_path().split('/')) == 4 and 'blog' in request.get_full_path() and 'slug' in view_kwargs:
            self.indicator = True
        else:
            self.indicator = False
        return None

    def process_template_response(self, request, response):
        if self.indicator:
            ccount_dict = {}
            c_dict = {}
            sups = SuperPostComment.objects.all()
            for i in sups:
                ccount_dict[i.id] = SubPostComment.objects.filter(super_comment=i.id).count()
                c_dict[i] = SubPostComment.objects.filter(super_comment=i.id)
            response.context_data['comments_count'] = ccount_dict
            response.context_data['comments'] = c_dict
        return response