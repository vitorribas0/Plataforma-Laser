from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from supabase import create_client


def _bucket():
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return client.storage.from_(settings.SUPABASE_STORAGE_BUCKET)


@deconstructible
class SupabaseMediaStorage(Storage):
    """Stores media files (e.g. client photos) in a private Supabase Storage bucket.

    Files are served through short-lived signed URLs rather than public links,
    since client photos are personal data. See core.management.commands.setup_supabase_storage
    for the one-time bucket provisioning step.
    """

    def _open(self, name, mode="rb"):
        data = _bucket().download(name)
        return ContentFile(data, name=name)

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        _bucket().upload(
            path=name,
            file=data,
            file_options={"content-type": _content_type(name), "upsert": "true"},
        )
        return name

    def exists(self, name):
        return _bucket().exists(name)

    def delete(self, name):
        _bucket().remove([name])

    def url(self, name):
        signed = _bucket().create_signed_url(name, settings.SUPABASE_STORAGE_SIGNED_URL_EXPIRY)
        return signed["signedURL"]

    def size(self, name):
        info = _bucket().info(name)
        return info.get("size", 0)


def _content_type(name):
    import mimetypes

    return mimetypes.guess_type(name)[0] or "application/octet-stream"
