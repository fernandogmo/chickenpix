from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.manager import BaseManager
from django.core.validators import RegexValidator
from uuid import uuid4
from django.conf import settings

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

class Album(Base):
     owner_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
     # archive_id = models.ForeignKey(Archive)
     is_private = models.BooleanField(default=True)

class Photo(Base):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    albums = models.ManyToManyField(Album)
    cloud_photo_link = models.URLField(unique=True)
    filename = models.FileField(MEDIA_ROOT='uploads/')

class ArchiveManager(models.Manager):
    def create_archive(self, album_id):
        if not album_id:
            raise ValueError('Album id is required')
        # TODO figure out compression
        photos = Photo.objects.get(album_id=album_id)
        # for photo in photos:
            # add photos to folder to archive then archive to whatever file name
        filename = 'lol.zip'

        archive = self.model(album_id=album_id, filename=filename)

        archive.save(using=self._db)
        return archive

class Archive(Base):
    filename = models.URLField(unique=True)
    album_id = models.ForeignKey(Album)

    objects = ArchiveManager()

class LinkManager(models.Manager):
    def create_link(self, archive_id):
        if not archive_id:
            raise ValueError('Archive id is required')

        url = 'http://localhost:8000/{}/'.format(uuid4())

        link = self.model(url=url, archive_id=archive_id)

        link.save(using=self._db)
        return link

class Link(Base):
    is_expired = models.BooleanField(default=False)
    url = models.URLField(unique=True)
    archive_id = models.ForeignKey(Archive)

    objects = LinkManager()
