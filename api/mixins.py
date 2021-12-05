from .serializers import WordsSerializer
from .utils import SmallPagesPagination

from rest_framework.permissions import IsAuthenticated


class WordsListMixin:

    pagination_class = SmallPagesPagination
    serializer_class = WordsSerializer

class PaginationPermissionMixin:

    pagination_class = SmallPagesPagination
    permission_classes = [IsAuthenticated]