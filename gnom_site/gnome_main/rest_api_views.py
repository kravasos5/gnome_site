from rest_framework.response import Response
from rest_framework.views import APIView
from gnom_site.gnome_main.models import PostComment
from gnom_site.gnome_main.serializers import PostCommentSerializer





class PostCommentAPI(APIView):
    '''ViewSet, который будет возвращать 10 новых комментариев'''
    # queryset = PostComment.objects.all()
    # serializer = PostCommentSerializer()

    def get(self, request):
        queryset = PostComment.objects.all()
        return Response({'get': PostCommentSerializer(queryset, many=True).data})