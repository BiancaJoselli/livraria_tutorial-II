from pyexpat import model

from django.db import models


class Editora(models.Model):
    nome = models.CharField(max_length=100)
    site = models.URLField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nome