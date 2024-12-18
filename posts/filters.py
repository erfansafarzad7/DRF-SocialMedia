from django_filters import rest_framework as filters
from posts.models import Post


class PostFilter(filters.FilterSet):
    """
    Filter for Posts by author username and tags.
    """

    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    tags = filters.CharFilter(method='filter_tags')

    class Meta:
        model = Post
        fields = ['author', 'tags']

    def filter_tags(self, queryset, name, value):
        """
        Custom filter to filter posts by tag names (comma-separated).
        """
        tag_names = value.split(',')
        return queryset.filter(tags__name__in=tag_names).distinct()
