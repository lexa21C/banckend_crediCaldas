from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Definición de opciones para roles
ROLES = (
    ('administrador', 'Administrador'),
    ('cobrador', 'Cobrador'),
)

# Modelo Perfil
class Perfil(models.Model):
    rol = models.CharField(max_length=30, choices=ROLES, unique=True, verbose_name="Rol")
    usuario = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name="Usuario")

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"

# Modelo Cliente
class Cliente(models.Model):
    nombre_completo = models.CharField(max_length=100, verbose_name="Nombre Completo")
    cliente_id = models.PositiveIntegerField(unique=True, verbose_name="ID del Cliente")
    num_ruta = models.PositiveIntegerField(verbose_name="Número de Ruta", blank=True, null=True)
    direccion = models.CharField(max_length=255, verbose_name="Dirección Principal")
    direccion_otra = models.CharField(max_length=255, verbose_name="Dirección Alternativa", blank=True, null=True)
    barrio = models.CharField(max_length=30, verbose_name="Barrio")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Ingrese un número de teléfono válido.")
    ])
    referencia = models.CharField(max_length=200, verbose_name="Referencia", blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

# Modelo Crédito
class Credito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="creditos", verbose_name="Cliente")
    fecha_prestamo = models.DateField(verbose_name="Fecha del Préstamo")
    saldo = models.IntegerField(verbose_name="Saldo")  # Cambiado a IntegerField
    prestamo = models.IntegerField(verbose_name="Monto del Préstamo")  # Cambiado a IntegerField

    FORMA_PAGO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ]
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES, verbose_name="Forma de Pago")
    numero_cuotas = models.PositiveIntegerField(verbose_name="Número de Cuotas")
    num_cuotas_pagadas = models.PositiveIntegerField(verbose_name="Número de Cuotas")

    ESTADO_CHOICES = [
        ('cancelado', 'Cancelado'),
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")
    cuotas_atrasadas = models.PositiveIntegerField(default=0, verbose_name="Cuotas Atrasadas")

    def __str__(self):
        return f"Crédito de {self.cliente.nombre_completo} - Saldo: {self.saldo} - Estado: {self.get_estado_display()}"

# Modelo Cuota
class Cuota(models.Model):
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name="cuotas", verbose_name="Crédito")
    fecha_pago = models.DateField(verbose_name="Fecha de Pago")
    fecha_pagada = models.DateField(null=True, blank=True, verbose_name="Fecha Pagada")
    valor = models.IntegerField(verbose_name="Valor de la Cuota")  # Sin max_digits
    valor_cancelado = models.IntegerField(verbose_name="Valor Cancelado", blank=True, null=True)  # Sin max_digits
    num_cuotas = models.PositiveIntegerField(verbose_name="Número de Cuotas")
    ESTADO_CHOICES = [
        ('cancelado', 'Cancelado'),
        ('pendiente', 'Pendiente de pago'),
        ('activo', 'Activo'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")

    def __str__(self):
        return f"Cuota {self.id} - Estado: {self.get_estado_display()} - Crédito {self.credito.id} - Crédito {self .valor_cancelado}"

class Cobro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    capital_inicial = models.PositiveIntegerField(verbose_name="Capital Inicial")
    capital_prestado = models.PositiveIntegerField(verbose_name="Capital Prestado")
    capital_cancelado = models.PositiveIntegerField(verbose_name="Capital Cancelado")
    capital_disponible = models.PositiveIntegerField(verbose_name="Capital Disponible")

    def __str__(self):
        return f"Cobro de {self.usuario.username} - Capital Disponible: {self.capital_disponible}"

# Modelo Gastos
class Gasto(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Gasto")
    valor = models.PositiveIntegerField(verbose_name="Valor del Gasto")
    fecha = models.DateField(verbose_name="Fecha del Gasto")

    def __str__(self):
        return f"Gasto: {self.nombre} - Valor: {self.valor}"

