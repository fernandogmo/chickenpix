from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.manager import BaseManager
from django.core.validators import RegexValidator
from uuid import uuid4
from django.conf import settings
import zipfile
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# Goal: Add this feature and uncomment it out
"""
phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Mobile number must be entered in the format:"
                                     " '+999999999'. Up to 15 digits allowed.")
"""

class MyUserManager(BaseUserManager):
    """
    Custom UserManager with email normalization
    """
    def create_user(self, email):
        """
        Creates and saves User
        """
        if not email:
            raise ValueError('Email is required')

        user = self.model(email=MyUserManager.normalize_email(email))
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    """
    Custom user model with email and email_verified
    fields
    """
    email = models.EmailField(max_length=255,
                              unique=True,
                              blank=True,
                              null=True)
    email_verified = models.BooleanField(default=False)

    # Goal: add this feature
    """
    mobile = models.CharField(validators=[phone_regex], max_length=15, unique=True, blank=True, null=True)
    mobile_verified = models.BooleanField(default=False)
    """

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

class Base(models.Model):
    """
    Base model for all models to inherit from.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AlbumManager(models.Manager):
    """ Naive manager """
    def create(self, title, owner_id):
        """
        Create album object with required parameters:
        title and owner_id.
        """
        if not title:
            raise ValueError('Title is required')
        if not owner_id:
            raise ValueError('Owner id is required')

        album = self.model(title=title,
                           owner_id=owner_id)
        album.save(using=self._db)
        return album

class Album(Base):
    """
    Album objects - each photo is linked to one or more Album.
    title and owner_id must be passed into object instantation.
    archive_id is updated after archive of album is created.
    is_private - True by default, users can choose to make their albums public.
    """
    title = models.CharField(max_length=100,
                             null=True)
    owner_id = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE)
    archive_id = models.ForeignKey('app.Archive',
                                   on_delete=models.CASCADE,
                                   null=True)
    is_private = models.BooleanField(default=True)

    def add_archive(self, archive):
        """
        Update album.archive_id with appropriate archive object.
        """
        self.archive_id = archive
        self.save()


class PhotoManager(models.Manager):
    """ Naive manager. """
    def create(self, filename, albums):
        if not filename:
            raise ValueError('Filename is required')

        photo = self.model(filename=filename)
        photo.save(using=self._db)
        return photo


class Photo(Base):
    """
    Photo class that stores all information
    related to each uploaded image.
    """
    # TODO: Figure out filepath. Currently this saves to uploads/uploads - we just want it to save to uploads/ - until we figure out S3 - when we will change the MEDIA_ROOT to s3.
    filename = models.ImageField(upload_to='photos/',
                                 default='image.jpg')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    albums = models.ManyToManyField(Album)
    thumbnail = models.ImageField(upload_to='thumbnails/',
                                  default='thumbnail.jpg')

    def save(self, *args, **kwargs):
        """
        Overrides default save() method by calling
        create_thumbnail before Photo object is saved.
        """
        if not self.create_thumbnail():
            raise Exception('Invalid file type')
        super(Photo, self).save(*args, **kwargs)

    def create_thumbnail(self):
        """
        Instance method to create thumbnail of Photo
        """
        thumbnail_name, thumbnail_extension = os.path.splitext(self.filename.name)
        thumbnail_extension = thumbnail_extension.lower()
        if thumbnail_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumbnail_extension == '.gif':
            FTYPE = 'GIF'
        elif thumbnail_extension == '.png':
            FTYPE = 'PNG'
        elif thumbnail_extension == '.bmp':
            FTYPE = 'BMP'
        else:
            return False
        image = Image.open(self.filename)
        image.thumbnail((400, 400))
        temp_thumbnail = BytesIO()
        image.save(temp_thumbnail, FTYPE)
        temp_thumbnail.seek(0)
        self.thumbnail.save('{}_thumbnail{}'.format(thumbnail_name,
                                                    thumbnail_extension),
                            ContentFile(temp_thumbnail.read()),
                            save=False)
        temp_thumbnail.close()
        return True


class ArchiveManager(models.Manager):
    """
    Manager for Archive objects - creates zip archive
    containing all photos within an album
    """
    def create(self, album_id):
        """
        Overrides create method of models.Manager
        by including compression of images.
        """
        if not album_id:
            raise ValueError('Album id is required')

        filename = os.path.join(settings.MEDIA_ROOT,
                                'zipfiles/{}.zip'.format(uuid4()))

        # Get a list of all filenames where album id matches the requested album
        photos = Photo.objects.filter(albums=album_id).values_list('filename',
                                                                   flat=True)

        # Compress all photos into one zip file
        with zipfile.ZipFile(filename, 'w') as archive:
            for photo in photos:
                photo = os.path.join(settings.MEDIA_ROOT,
                                     photo)
                archive.write(photo, os.path.relpath(photo,
                                                     settings.MEDIA_ROOT))

        archive = self.model(album_id=album_id,
                             filename=filename)
        archive.save(using=self._db)
        return archive


class Archive(Base):
    """
    Class for archive objects containing
    file name and foreign key for album.
    """
    filename = models.URLField(unique=True)
    album_id = models.ForeignKey(Album,
                                 on_delete=models.CASCADE)

    objects = ArchiveManager()


class LinkManager(models.Manager):
    """
    Manager to create Link objects
    """
    def create(self, archive):
        """
        Overrides default create method to include url
        creation for each archive.
        """
        if not archive:
            raise ValueError('Archive id is required')

        # TODO - finalize URL name and edit download route and HTML based on final URL
        # url = 'http://localhost:8000/download/{}/{}/'.format(archive.id, uuid4())
        host = settings.ALLOWED_HOSTS[0]
        if host == 'localhost':
            host += ':8000'
        url = f'http://{host}/download/{archive.id}/{uuid4()}/'

        link = self.model(url=url, archive_id=archive)
        link.save(using=self._db)
        return link


class Link(Base):
    """
    Link class containing URL, is_expired,
    and archive_id Foreign Key for related archives.
    """
    is_expired = models.BooleanField(default=False)
    url = models.URLField(unique=True)
    archive_id = models.ForeignKey(Archive, on_delete=models.CASCADE)

    objects = LinkManager()
