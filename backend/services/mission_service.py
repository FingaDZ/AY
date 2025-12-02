from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Mission, MissionClientDetail, MissionLogisticsMovement, Client, Employe, Parametre
from schemas.mission import MissionCreate, MissionClientDetailCreate
from decimal import Decimal

class MissionService:
    def __init__(self, db: Session):
        self.db = db

    def get_tarif_km(self) -> Decimal:
        param = self.db.query(Parametre).filter(Parametre.cle == "tarif_km").first()
        if not param:
            param = Parametre(
                cle="tarif_km",
                valeur="3.00",
                description="Tarif kilométrique pour les missions (DA/km)"
            )
            self.db.add(param)
            self.db.commit()
        return Decimal(param.valeur)

    def create_mission(self, mission_in: MissionCreate) -> Mission:
        # 1. Validate Chauffeur
        chauffeur = self.db.query(Employe).filter(Employe.id == mission_in.chauffeur_id).first()
        if not chauffeur:
            raise HTTPException(status_code=404, detail="Chauffeur non trouvé")
        
        # 2. Determine Main Client (Legacy Support)
        main_client_id = mission_in.client_id
        if not main_client_id and mission_in.clients:
            main_client_id = mission_in.clients[0].client_id
        
        if not main_client_id:
             raise HTTPException(status_code=400, detail="Au moins un client est requis")

        main_client = self.db.query(Client).filter(Client.id == main_client_id).first()
        if not main_client:
            raise HTTPException(status_code=404, detail="Client principal non trouvé")

        # 3. Calculate Prime (Legacy Logic - based on main client for now)
        # In a multi-client scenario, we might want to sum distances, but for now let's stick to the main client's distance
        # or maybe the user enters a total distance? The current model takes distance from Client.
        tarif_km = main_client.tarif_km
        distance = main_client.distance
        prime_calculee = distance * tarif_km

        # 4. Create Mission
        db_mission = Mission(
            date_mission=mission_in.date_mission,
            chauffeur_id=mission_in.chauffeur_id,
            client_id=main_client_id,
            distance=distance,
            tarif_km=tarif_km,
            prime_calculee=prime_calculee
        )
        self.db.add(db_mission)
        self.db.flush() # Get ID

        # 5. Create Client Details
        if mission_in.clients:
            for client_detail in mission_in.clients:
                self._create_client_detail(db_mission.id, client_detail)
        else:
            # Create a default detail for the main client if no details provided (backward compatibility)
            default_detail = MissionClientDetail(
                mission_id=db_mission.id,
                client_id=main_client_id
            )
            self.db.add(default_detail)

        self.db.commit()
        self.db.refresh(db_mission)
        return db_mission

    def _create_client_detail(self, mission_id: int, detail_in: MissionClientDetailCreate):
        db_detail = MissionClientDetail(
            mission_id=mission_id,
            client_id=detail_in.client_id,
            montant_encaisse=detail_in.montant_encaisse,
            statut_versement=detail_in.statut_versement,
            observations=detail_in.observations
        )
        self.db.add(db_detail)
        self.db.flush()

        for movement in detail_in.logistics:
            db_movement = MissionLogisticsMovement(
                mission_client_detail_id=db_detail.id,
                logistics_type_id=movement.logistics_type_id,
                quantity_out=movement.quantity_out,
                quantity_in=movement.quantity_in
            )
            self.db.add(db_movement)

    def update_mission(self, mission_id: int, mission_in: MissionCreate) -> Mission:
        db_mission = self.db.query(Mission).filter(Mission.id == mission_id).first()
        if not db_mission:
            raise HTTPException(status_code=404, detail="Mission non trouvée")

        # Update basic fields
        db_mission.date_mission = mission_in.date_mission
        db_mission.chauffeur_id = mission_in.chauffeur_id
        
        # Update Main Client (Legacy)
        main_client_id = mission_in.client_id
        if not main_client_id and mission_in.clients:
            main_client_id = mission_in.clients[0].client_id
        
        if main_client_id:
            client = self.db.query(Client).filter(Client.id == main_client_id).first()
            if client:
                db_mission.client_id = main_client_id
                db_mission.distance = client.distance
                db_mission.tarif_km = client.tarif_km
                db_mission.prime_calculee = client.distance * client.tarif_km

        # Update Details: Full Replace Strategy for simplicity
        # Delete existing details
        self.db.query(MissionClientDetail).filter(MissionClientDetail.mission_id == mission_id).delete()
        
        # Re-create details
        if mission_in.clients:
            for client_detail in mission_in.clients:
                self._create_client_detail(mission_id, client_detail)
        elif main_client_id:
             # Default detail if none provided
            default_detail = MissionClientDetail(
                mission_id=mission_id,
                client_id=main_client_id
            )
            self.db.add(default_detail)

        self.db.commit()
        self.db.refresh(db_mission)
        return db_mission
