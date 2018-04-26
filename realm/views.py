from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realm.serializers import RealmSerializer


class SetRealmAPIView(APIView):
    serializer_class = RealmSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        serializer = RealmSerializer(
            request.data,
            context={'user': request.user}
        )
        return Response(serializer.data)
