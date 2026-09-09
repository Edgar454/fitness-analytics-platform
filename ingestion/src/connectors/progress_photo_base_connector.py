from abc import ABC, abstractmethod
from ingestion.src.connectors.models.progress_photo_record import ProgressPhotoRecord

class ProgressPhotoBaseConnector(ABC):
    """
    Contrat dédié au domaine progress_photos.
    Contrairement à BaseConnector (fetch -> transform), ce domaine implique un
    vrai transfert binaire : téléchargement depuis la source tierce, puis upload
    vers notre propre S3, avant de pouvoir produire un ProgressPhotoRecord.
    """

    connector_name: str  # ex: "lyfta"

    @abstractmethod
    def list_available_photos(self, since, until) -> list[dict]:
        """Liste les photos disponibles côté source (métadonnées + URL/référence source), sans les télécharger."""
        raise NotImplementedError

    @abstractmethod
    def sync_photo(self, source_photo: dict) -> "ProgressPhotoRecord":
        """
        Télécharge le binaire depuis la source, l'uploade vers notre S3,
        et retourne le ProgressPhotoRecord résultant (avec le s3_key définitif).
        """
        raise NotImplementedError

    def run(self, since, until) -> list["ProgressPhotoRecord"]:
        """Point d'entrée appelé par l'orchestrateur."""
        available = self.list_available_photos(since, until)
        return [self.sync_photo(photo) for photo in available]