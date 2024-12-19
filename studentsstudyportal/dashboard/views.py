from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError
from django.contrib.auth import logout

# Create your views here.


# Home
def home(request):
    return render(request, 'dashboard/home.html')

# Notes
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description = request.POST['description'])
            notes.save()
        
        messages.success(request, f'Notes added from {request.user.username} successfully')
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user = request.user)
    context = {'notes':notes, 'form':form}
    return render(request, 'dashboard/notes.html', context)

# Delete Notes
def delete_notes(request, pk=None):
    Notes.objects.get(id=pk).delete()
    messages.success(request, f'Notes deleted from {request.user.username} successfully')
    return redirect('/notes/')

class NotesDetailView(generic.DetailView):
    model = Notes

# Homework
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished,
            )
            homeworks.save()
            messages.success(request, f'Homework added from {request.user.username}!!')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user = request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks':homework, 'homeworks_done':homework_done, 'form':form}
    return render(request, 'dashboard/homework.html', context)

# Update Homework
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')


# Delete Homework
def delete_homework(request, pk):
    Homework.objects.get(id=pk).delete()
    messages.success(request, f'Homework deleted by {request.user.username}!!')
    return redirect('/homework/')


# YouTube Section
def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'viewcount':i['viewCount']['short'],
                'publishedTime':i['publishedTime'],
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {
                'form':form,
                'results':result_list
            }
        return render(request, 'dashboard/youtube.html', context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/youtube.html',context)

# Todo Function
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished,
            )
            todos.save()
            messages.success(request, f"Todo added from {request.user.username}!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done,
    }
    return render(request, 'dashboard/todo.html', context)

# Update Todo
def update_todo(request, pk):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('/todo/')



# Delete Todo
def delete_todo(request, pk):
    Todo.objects.get(id=pk).delete()
    messages.success(request, f"Todo deleted successfully from {request.user.username}!!")
    return redirect('/todo/')


# Books Section
def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://www.googleapis.com/books/v1/volumes?q='+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context = {
                'form':form,
                'results':result_list,
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)

# Dictonary Section
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/'+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/dictionary.html', context)


# Wikipedia Section
def wiki(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        try:
            search = wikipedia.page(text)
            context = {
                'form':form,
                'title':search.title,
                'link':search.links,
                'details':search.summary
            }
        except DisambiguationError as e:
            # Handle ambigious search term
            context = {
                'form':form,
                'error':f"The term '{text}' is ambgious. Please be more specific!!",
                'options':e.options  # Provide list of options for disambgious
            }
        except PageError:
            # Handle page not found error
            context = {
                'form': form,
                'error': f'No Wikipedia page found for "{text}".'
            }
        except Exception as e:
            # Handle other possible errors
            context = {
                'form': form,
                'error': 'An error occurred: ' + str(e)
            }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request, 'dashboard/wiki.html', context)


# Conversion Section
def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        
        # Length conversion logic
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']  # Corrected typo: 'messure2' -> 'measure2'
                input_value = request.POST['input']
                answer = ''
                
                if input_value and float(input_value) >= 0:
                    input_value = float(input_value)
                    if first == 'yard' and second == 'foot':
                        answer = f'{input_value} yard = {input_value * 3} foot'
                    elif first == 'foot' and second == 'yard':
                        answer = f'{input_value} foot = {input_value / 3} yard'
                    
                context['answer'] = answer
        
        # Mass conversion logic
        elif request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']  # Corrected typo: 'messure2' -> 'measure2'
                input_value = request.POST['input']
                answer = ''
                
                if input_value and float(input_value) >= 0:
                    input_value = float(input_value)
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input_value} pound = {input_value * 0.453592} kilogram'
                    elif first == 'kilogram' and second == 'pound':  # Corrected conversion logic
                        answer = f'{input_value} kilogram = {input_value * 2.20462} pound'
                
                context['answer'] = answer
    
    # Handle GET requests
    else:
        form = ConversionForm()
        context = {
            'form': form,
            'input': False
        }
    
    return render(request, 'dashboard/conversion.html', context)




# Register
def register(request):
    if request.method == 'POST':
        form = UserRegistrartionForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!!")
            return redirect('login')
    else:
        form = UserRegistrartionForm()
    context = {
        'form':form
    }
    return render(request, 'dashboard/register.html', context)



# Profile
def profile(request):
    homework = Homework.objects.filter(is_finished = False, user = request.user)
    todo = Todo.objects.filter(is_finished = False, user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks':homework,
        'todos':todo,
        'homework_done':homework_done,
        'todos_done':todos_done
    }
    return render(request, 'dashboard/profile.html', context)







