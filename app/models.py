from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.manager import BaseManager
from django.core.validators import RegexValidator
from uuid import uuid4
from django.conf import settings
import zipfile
import os

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Mobile number must be entered in the format:"
                                     " '+999999999'. Up to 15 digits allowed.")

class MyUserManager(BaseUserManager):
    def create_user(self, email):
        """
        Creates and saves User
        """
        if not email:
            raise ValueError('Email is required')

        user = self.model(email=MyUserManager.normalize_email(email),
                )

        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    #mobile = models.CharField(validators=[phone_regex], max_length=15, unique=True, blank=True, null=True)
    #mobile_verified = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AlbumManager(models.Manager):
    """ Naive manager """
    def create(self, title, owner_id):
        if not title:
            raise ValueError('Title is required')
        if not owner_id:
            raise ValueError('Owner id is required')
        """
        if not archive_id:
            raise ValueError('Archive id is required')
        """
        album = self.model(title=title, owner_id=owner_id)

        album.save(using=self._db)
        return album

class Album(Base):
    title = models.CharField(max_length=100, null=True)
    owner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # archive_id = models.ForeignKey('app.Archive', on_delete=models.CASCADE)
    is_private = models.BooleanField(default=True)

class PhotoManager(models.Manager):
    """ Naive manager. """
    def create(self, filename, users, albums, link):
        if not filename:
            raise ValueError('Filename is required')
        if not users:
            raise ValueError('Users is required')
        if not albums:
            raise ValueError('Albums is required')
        if not link:
            raise ValueError('Link is required')

        photo = self.model(filename=filename,
                users=users)
        photo.save(using=self._db)
        return photo

class Photo(Base):
    # TODO: Figure out filepath. Currently this saves to uploads/uploads - we just want it to save to uploads/ - until we figure out S3 - when we will change the MEDIA_ROOT to s3.
    filename = models.ImageField(upload_to=settings.MEDIA_ROOT, default='None/lol.jpg')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    # TODO: change to ManyToManyField and revert to non-nullable
    albums = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    # albums = models.ManyToManyField(Album)
    # cloud_photo_link = models.URLField(unique=True)

class ArchiveManager(models.Manager):
    def create(self, album_id):
        if not album_id:
            raise ValueError('Album id is required')

        filename = os.path.join(settings.MEDIA_ROOT, 'zipfiles/{}.zip'.format(uuid4()))

        # Get a list of all filenames where album id matches the requested album
        photos = Photo.objects.filter(albums=album_id).values_list('filename', flat=True)

        # Compress all photos into one zip file
        with zipfile.ZipFile(filename, 'w') as archive:
            for photo in photos:
                photo = os.path.join(settings.MEDIA_ROOT, photo)
                archive.write(photo)

        archive = self.model(album_id=album_id, filename=filename)

        archive.save(using=self._db)
        return archive

class Archive(Base):
    filename = models.URLField(unique=True)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)

    objects = ArchiveManager()

class LinkManager(models.Manager):
    # changed to archive from archive_id so we can say "archive.id" instead of "archive_id.id" on line 125
    def create(self, archive):
        if not archive:
            raise ValueError('Archive id is required')

        # TODO - finalize URL name and edit download route and HTML based on final URL
        url = 'http://localhost:8000/download/{}/{}/'.format(archive.id, uuid4())

        link = self.model(url=url, archive_id=archive)

        link.save(using=self._db)
        return link

class Link(Base):
    is_expired = models.BooleanField(default=False)
    url = models.URLField(unique=True)
    archive_id = models.ForeignKey(Archive, on_delete=models.CASCADE)

    objects = LinkManager()
