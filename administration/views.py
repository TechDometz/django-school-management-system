from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AcademicYear, Term, Article, CarouselImage
from .serializers import (
    AcademicYearSerializer,
    TermSerializer,
    ArticleSerializer,
    CarouselImageSerializer,
)


# Article Views
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]


# CarouselImage Views
class CarouselImageListCreateView(generics.ListCreateAPIView):
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer
    permission_classes = [IsAuthenticated]


class CarouselImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer
    permission_classes = [IsAuthenticated]


# AcademicYear Views
class AcademicYearListCreateView(generics.ListCreateAPIView):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]


class AcademicYearDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]


# Term Views
class TermListCreateView(generics.ListCreateAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated]


class TermDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated]
