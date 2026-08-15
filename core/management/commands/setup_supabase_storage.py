from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from storage3.exceptions import StorageApiError
from supabase import create_client


class Command(BaseCommand):
    help = "Creates the private Supabase Storage bucket used for media files, if it doesn't already exist."

    def handle(self, *args, **options):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise CommandError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set (run `vercel env pull .env.local` first)."
            )

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        bucket_id = settings.SUPABASE_STORAGE_BUCKET

        try:
            client.storage.get_bucket(bucket_id)
            self.stdout.write(self.style.SUCCESS(f"Bucket '{bucket_id}' already exists."))
            return
        except StorageApiError as exc:
            is_not_found = str(getattr(exc, "status", "")) == "404" or "not found" in str(
                getattr(exc, "message", exc)
            ).lower()
            if not is_not_found:
                raise

        client.storage.create_bucket(
            bucket_id,
            options={
                "public": False,
                "file_size_limit": "5MB",
                "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Bucket '{bucket_id}' created (private)."))
