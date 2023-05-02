
# import all models so that they are registered with the database
from .models import db, User, Category, Book, Video, BookDownload, Rental, AccessRequest, DownloadRequest

# import all forms
from .forms import CategoryForm, BookForm, VideoForm, ProfileForm, ChangePasswordForm 
