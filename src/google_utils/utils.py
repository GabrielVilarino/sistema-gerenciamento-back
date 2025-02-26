from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from io import BytesIO
from googleapiclient.http import MediaIoBaseUpload
import os
# Arquivo JSON com as credenciais da API do Google Drive
SERVICE_ACCOUNT_FILE = "sistema-templaria-b6473a2412fc.json"

# ID da pasta onde os arquivos serão armazenados no Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")


def delete_from_google_drive(file_id: str) -> bool:
    """
    Exclui uma imagem do Google Drive pelo ID.
    """
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])
        service = build("drive", "v3", credentials=creds)

        service.files().delete(fileId=file_id).execute()
        print(f"Arquivo {file_id} excluído com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao excluir arquivo do Google Drive: {e}")
        return False


def upload_to_google_drive(filename: str, file_bytes: bytes, mime_type: str, old_file_id: str = None) -> str:
    """
    Faz upload da imagem para o Google Drive, excluindo a anterior se necessário, e retorna a URL pública.
    """
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])
        service = build("drive", "v3", credentials=creds)

        # Exclui a imagem antiga, se fornecida
        if old_file_id:
            response_delete = delete_from_google_drive(old_file_id)

            if not response_delete:
                print(f"Erro ao deletar imagem no Google Drive: {e}")
                return None

        # Criar o arquivo no Google Drive
        file_metadata = {
            "name": filename,
            "parents": [GOOGLE_DRIVE_FOLDER_ID]  # Define a pasta de destino
        }

        media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # Tornar o arquivo público
        service.permissions().create(
            fileId=file["id"],
            body={"role": "reader", "type": "anyone"},
        ).execute()

        # Retornar a URL do arquivo
        file_url = f"https://drive.google.com/uc?id={file['id']}"
        return file_url

    except Exception as e:
        print(f"Erro ao fazer upload para o Google Drive: {e}")
        return None
    

