class AppError(Exception):
    """Basisklasse für fachliche und technische Fehler."""


class ConfigurationError(AppError):
    """Fehler in der lokalen Konfiguration."""


class DependencyError(AppError):
    """Fehlende Laufzeitabhängigkeit."""


class RepositoryError(AppError):
    """Fehler im Datenzugriff."""


class ValidationError(AppError):
    """Ungültige Benutzereingabe oder verletzte Fachregel."""
