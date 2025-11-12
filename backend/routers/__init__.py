from .employes import router as employes_router
from .pointages import router as pointages_router
from .clients import router as clients_router
from .missions import router as missions_router
from .avances import router as avances_router
from .credits import router as credits_router
from .salaires import router as salaires_router
from .rapports import router as rapports_router
from .parametres import router as parametres_router
from .utilisateurs import router as utilisateurs_router

__all__ = [
    "employes",
    "pointages",
    "clients",
    "missions",
    "avances",
    "credits",
    "salaires",
    "rapports",
    "parametres",
    "utilisateurs",
]
