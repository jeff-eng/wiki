import markdown2, re, random

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import util

def index(request):
    return render(request, 'encyclopedia/index.html', {
        'entries': util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if entry:
        # Convert the markdown to HTML
        html = markdown2.markdown(entry)
        return render(request, 'encyclopedia/entry.html', {
            'html': html,
            'title': title
        })
    else:
        # Render an error page
        return render(request, 'encyclopedia/error.html', {
            'error_code': 404,
            'error_message': 'Page Not Found'
        })

def search(request):
    if request.method == 'POST':
        # Obtain user input from search box
        query = request.POST['query']
        
        # Direct user to page if there is exact match, otherwise display list of matches
        if util.get_entry(query):
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': query}))
        else:
            entries = util.list_entries()
            matching_entries = list()
            for entry in entries:
                if re.search(query, entry, re.IGNORECASE):
                    matching_entries.append(entry)
            return render(request, 'encyclopedia/search_results.html', {
                'matches': matching_entries,
                'query': query
            })

def new(request):
    return render(request, 'encyclopedia/new_page.html')

def save(request):
    if request.method == 'POST':
        title = request.POST['title'].strip()
        content = request.POST['wiki-content']

        # Check if entry already exists, otherwise save to disk
        if util.get_entry(title):
            return render(request, 'encyclopedia/error.html', {
                'error_code': 403,
                'error_message': 'Forbidden - Page Already Exists'
            })
        else:
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': title}))
    else:
        return render(request, 'encyclopedia/error.html', {
            'error_code': 404,
            'error_message': 'Page Not Found'
        })

def random_page(request):
    entries = util.list_entries()
    
    if entries:
        random_selection = random.choice(entries)
        return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': random_selection}))
    else:
        return render(request, 'encyclopedia/error.html', {
            'error_code': 404,
            'error_message': 'It\'s not you, it\'s us.'
        })

def edit_page(request, title):  
    if request.method == 'GET':
        return render(request, 'encyclopedia/edit.html', {
            'title': title,
            'content': util.get_entry(title)
        })
    elif request.method == 'POST':
        util.save_entry(title, request.POST['wiki-content'])
        return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': title}))
    else:
        return render(request, 'encyclopedia/error.html', {
            'error_code': 404,
            'error_message': 'Page Not Found'
        })