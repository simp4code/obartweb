from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
#from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from .forms import VideoContentForm
from .models import VideoContent,GeneratedCode
import os
from django.conf import settings
from django.db.models import F
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def remove_old_codes(request):
    # Remove codes older than 4 hours
    old_codes = GeneratedCode.objects.filter(created_at__lt=timezone.now() - timezone.timedelta(hours=4))
    old_codes.delete()

    return HttpResponseRedirect(reverse('check_codes'))

def verify_codes(request):
    if request.method == 'POST':
        code = request.POST.get('code',None)
        if code:
            if GeneratedCode.objects.filter(code=code).exists():
                return redirect('home')
            else:
                error_message = "Invalid code. Please try again."
                return render(request, 'ask_code.html', {'error_message': error_message})

    return render(request, 'ask_code.html')

def generate_code(request):
    if request.method == 'POST':
        # Generate a 9-digit code
        code = get_random_string(length=9, allowed_chars='1234567890')

        # Save the code to the database
        GeneratedCode.objects.create(code=code)


        # Redirect to the check_codes view to display the generated codes
        return redirect('check_codes')
    
    return render(request, 'codes.html')

def check_codes(request):
    generated_codes = GeneratedCode.objects.all()
    context= {
        'generated_codes':generated_codes,
    }
    return render(request, 'codes.html', context)

def ask_code(request):
    return render(request,'ask_code.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            # Handle empty fields
            return render(request, 'login.html', {'error': 'Please fill in both username and password fields.'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Change 'home' to the name of your home URL
        elif username == "admin" and password == "adminpass":
            return redirect('admin_page')
        else:
            # Handle invalid login
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate user until email confirmation
            user.save()
            # Send verification email
            send_verification_email(request, user)
            return redirect('login')  # Redirect to login page after successful sign-up
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def send_verification_email(request, user):
    subject = 'Activate Your Account'
    message = render_to_string('verification_email.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': user.id,
    })
    plain_message = strip_tags(message)
    from_email = 'ObartWeb <lomonsod.karim@yahoo.com>'  # Replace with your Yahoo email address
    to_email = user.username

    try:
        send_mail(subject, plain_message, from_email, [to_email], html_message=message,
                  fail_silently=False)
    except Exception as e:
        return HttpResponse(f'An error occurred: {str(e)}')
    else:
        return HttpResponse('Email sent successfully!')

def activate_account(request, uid):
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None

    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been successfully activated. You can now login.')
        return redirect('login')
    else:
        return HttpResponse('Invalid activation link')

def user_logout(request):
    logout(request)
    return redirect('index')


def index(request):
    return render(request, 'index.html')


def homepage(request):
    # Fetch chapters and videos data
    chapters = {}  # Initialize an empty dictionary to store chapters and videos
    for chapter_number, chapter_name in VideoContent.CHAPTER_CHOICES:
        # Fetch videos for each chapter and store them in the dictionary
        videos = VideoContent.objects.filter(chapter=chapter_number)
        chapters[chapter_name] = videos.annotate(chapter_name=F('chapter'))

    # Get the logged-in user's email
    user_email = None
    if request.user.is_authenticated:
        user_email = request.user.username

    context = {
        'chapters': chapters,
        'user_email': user_email  # Pass the user's email to the template
    }
    return render(request, 'homepage.html', context)

def admin_page(request):
    # Fetch chapters and videos data
    chapters = {}  # Initialize an empty dictionary to store chapters and videos
    for chapter_number, chapter_name in VideoContent.CHAPTER_CHOICES:
        # Fetch videos for each chapter and store them in the dictionary
        videos = VideoContent.objects.filter(chapter=chapter_number)
        chapters[chapter_name] = list(videos)

    # Get the logged-in user's email
    user_email = None
    if request.user.is_authenticated:
        user_email = request.user.username

    context = {
        'chapters': chapters,
        'user_email': user_email  # Pass the user's email to the template
    }
    return render(request, 'admin_page.html', context)


def add_video_content(request):
    if request.method == 'POST':
        form = VideoContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_page')  # Redirect to a success URL
    else:
        form = VideoContentForm()
    return render(request, 'add_video.html', {'form': form})
    

def update_video(request, video_id):
    video = get_object_or_404(VideoContent, pk=video_id)
    
    if request.method == 'POST':
        form = VideoContentForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            # Delete the old video file before saving the form
            old_video_path = video.video.path
            form.save()

            # Check if the video file has changed
            new_video_path = form.cleaned_data.get('video').path
            if old_video_path != new_video_path:
                # Delete the old video file from the "videos/" folder
                os.remove(old_video_path)

            return redirect('admin_page')  # Redirect to the index page or any other page
    else:
        form = VideoContentForm(instance=video)
    
    return render(request, 'update_video.html', {'form': form, 'video': video})

def delete_video(request, video_id):
    video = get_object_or_404(VideoContent, pk=video_id)
    
    if request.method == 'POST':
        # Delete the video file from the "videos/" folder
        video_path = video.video.path
        os.remove(video_path)

        # Delete the VideoContent instance from the database
        video.delete()

        return redirect('admin_page')  # Redirect to the index page or any other page
    
    return render(request, 'delete_video.html', {'video': video})

def video_list(request):
    video_folder = os.path.join(settings.BASE_DIR, 'videos')
    videos = os.listdir(video_folder)
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, video_id):
    # Retrieve the VideoContent object based on the video_id
    video = get_object_or_404(VideoContent, pk=video_id)
    # Pass the video object to the template
    return render(request, 'video_detail.html', {'video': video})