

# Create your models here.
from django.db import models
<<<<<<< HEAD
=======
from django.contrib.auth.models import User

class NotaPersonal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    texto = models.TextField()
    
    def __str__(self):
        return f"Nota de {self.usuario.username} para {self.fecha}" 
>>>>>>> 70c3a41 (Añadir .gitignore para entorno virtual, archivos temporales y configuración de usuario)

class Habilidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class OfertaLaboral(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    empresa = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=200)
    fecha_publicacion = models.DateField()
    habilidades = models.ManyToManyField(Habilidad)
    salario = models.CharField(max_length=100, blank=True, null=True)
    url_oferta = models.URLField()  # Enlace a la oferta original en el portal
    portal = models.CharField(max_length=100)  # Ejemplo: 'LinkedIn', 'Indeed', etc.

    def __str__(self):
        return self.titulo

<<<<<<< HEAD
=======
class InscripcionOferta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    oferta = models.ForeignKey(OfertaLaboral, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} -> {self.oferta.titulo}"

class DatoMercado(models.Model):
    fecha = models.DateField()
    region = models.CharField(max_length=100, blank=True, null=True)
    industria = models.CharField(max_length=100, blank=True, null=True)
    habilidad = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=0)
    portal = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.habilidad} ({self.region}, {self.industria}) - {self.fecha}"
>>>>>>> 70c3a41 (Añadir .gitignore para entorno virtual, archivos temporales y configuración de usuario)

