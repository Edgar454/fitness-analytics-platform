from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ProgressPhotoRecord:
    """
    Sortie standardisée attendue de tout connector du domaine progress_photos.
    Contrairement aux autres domaines, le connector doit avoir déjà rapatrié
    le binaire et l'avoir uploadé vers S3 avant de retourner ce record —
    s3_key référence toujours notre propre stockage, jamais un lien externe.
    """

    s3_key: str
    view: Optional[str] = None  
    mime_type: Optional[str] = None
    uploaded_at: Optional[datetime] = None