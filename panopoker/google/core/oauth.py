from authlib.integrations.starlette_client import OAuth
from panopoker.core.config import settings

oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=settings.GOOGLE_WEB_CLIENT_ID,
    client_secret=settings.GOOGLE_WEB_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
