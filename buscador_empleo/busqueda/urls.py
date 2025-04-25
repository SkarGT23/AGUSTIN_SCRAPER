from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('buscar-empleo/', views.buscar_empleo, name='buscar'),  # Cambiado a 'buscar-empleo'
    path('buscar-ofertas/', views.buscar_ofertas, name='buscar_ofertas'),  # Cambiado a 'buscar-ofertas'
]

=======
    path('dashboard/', views.dashboard_ia, name='dashboard_ia'),
    path('analisis/', views.analisis_mercado, name='analisis_mercado'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),  # Página principal
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('buscar/linkedin/', views.buscar_linkedin, name='buscar_linkedin'),
    path('buscar/tecnoempleo/', views.buscar_tecnoempleo, name='buscar_tecnoempleo'),
    path('buscar/infojobs/', views.buscar_infojobs, name='buscar_infojobs'),
    path('buscar/todos/', views.buscar_todos, name='buscar_todos'),
    path('buscar-ofertas/', views.buscar_ofertas, name='buscar_ofertas'),
    path('calendario/', views.calendario, name='calendario'),
    path('perfil/', views.perfil, name='perfil'),
]
>>>>>>> 70c3a41 (Añadir .gitignore para entorno virtual, archivos temporales y configuración de usuario)
