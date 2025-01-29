from django.urls import path

from administration.views import (
    ArticleListCreateView,
    ArticleDetailView,
    CarouselImageListCreateView,
    CarouselImageDetailView,
)


urlpatterns = [
    # Article URLs
    path("articles/", ArticleListCreateView.as_view(), name="article-list-create"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    # Carousel Image URLs
    path(
        "carousel-images/",
        CarouselImageListCreateView.as_view(),
        name="carousel-image-list-create",
    ),
    path(
        "carousel-images/<int:pk>/",
        CarouselImageDetailView.as_view(),
        name="carousel-image-detail",
    ),
]
