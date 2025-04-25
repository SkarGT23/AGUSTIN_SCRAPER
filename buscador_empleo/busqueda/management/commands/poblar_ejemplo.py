from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from busqueda.models import OfertaLaboral, Habilidad, DatoMercado, InscripcionOferta
from datetime import datetime
import random

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para análisis y dashboards'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        usuario, _ = User.objects.get_or_create(username='ejemplo', defaults={'email': 'ejemplo@demo.com'})

        # Habilidades
        habilidades = ['Python', 'Django', 'React', 'SQL', 'AWS', 'Docker', 'Java', 'JavaScript']
        habilidad_objs = [Habilidad.objects.get_or_create(nombre=h)[0] for h in habilidades]

        # Ofertas
        portales = ['Tecnoempleo', 'InfoJobs', 'LinkedIn']
        empresas = ['EmpresaA', 'EmpresaB', 'EmpresaC']
        for mes in ['2025-01', '2025-02', '2025-03', '2025-04']:
            for i in range(3):
                oferta = OfertaLaboral.objects.create(
                    titulo=f"Oferta {i+1} {mes}",
                    empresa=random.choice(empresas),
                    portal=random.choice(portales),
                    fecha_publicacion=datetime.strptime(mes+'-01', '%Y-%m-%d')
                )
                oferta.habilidades.set(random.sample(habilidad_objs, k=2))

        # Datos de mercado
        for region in ['Madrid', 'Barcelona']:
            for ind in ['IT', 'Finanzas']:
                for h in habilidad_objs:
                    DatoMercado.objects.create(
                        fecha=datetime.strptime('2025-04-01', '%Y-%m-%d'),
                        region=region,
                        industria=ind,
                        habilidad=h.nombre,
                        cantidad=random.randint(10, 60)
                    )

        # Inscripciones
        for oferta in OfertaLaboral.objects.all():
            InscripcionOferta.objects.create(
                usuario=usuario,
                oferta=oferta
            )

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo creados correctamente.'))
