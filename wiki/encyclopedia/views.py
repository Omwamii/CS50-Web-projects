from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import util
import markdown
from django.db.models import Q
from .models import Page
from .forms import PageForm
from django.contrib import messages
import random


def index(request):
    """ render the index default page with entries
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def get_wiki(request, name):
    """ display wiki page content when url clicked
    """
    content = util.get_entry(name)
    if content == None:
         page = get_object_or_404(Page, title=name)
         if page:
             content = markdown.markdown(page.content)
         else:
             content = markdown.markdown(f"## {name.capitalize()}\'s page has not been found")
    else:
        content = markdown.markdown(content)
    return render(request, "encyclopedia/content.html", {
        "content": content,
        "title": name
        }) 

def search(request):
    """ search for wiki page when user enters query on searchbox
    """
    query = request.GET.get('q')
    if query:
        page = util.get_entry(query)
        if page:
            # If matching page, redirect to it
            content = markdown.markdown(page)
            return render(request, "encyclopedia/content.html", {
                "content": content,
                "title": query
                })
        else:
            page = Page.objects.filter(title=query)
            if page:
                content = markdown.markdown(page.content)
                return render(request, "encyclopedia/content.html", {
                    "content": content,
                    "title": query
                    })
            else:
                pages = Page.objects.filter(Q(title__icontains=query))
                results = list()
                for page in pages:
                    results.append(page.title)
                entries = util.list_entries()
                for entry in entries:
                    if entry.lower().__contains__(query):
                        results.append(entry)
                if len(results) > 0:
                    # return list of results to search page
                    print(results)  # for debugging
                    return render(request, "encyclopedia/search.html", {"results": results, "query": query})
                else:
                    # If no matching page, render message saying so
                    message = f"No pages found matching '{query}'."
                    return render(request, 'encyclopedia/search.html', {'message': message})


def create_page(request):
    """ render template for user to create new page content
    """
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid:
            # if form is valid, save if entry doesn't exist
            p_title = request.POST['title']
            p_content = request.POST['content']
            old_files = util.list_entries()
            if p_title in old_files:
                # render message to the user 'title exists'
                messages.error(request, 'Page title already exists')
                return redirect('create_page')
            else:
                util.save_entry(p_title, p_content)  # save entry to disk
                content = markdown.markdown(p_content)
                return render(request, "encyclopedia/content.html", {
                    "content": content,
                    "title": p_title
                    })
        else:
            messages.error(request, 'Form is invalid')
            return redirect('create_page')
    else:  # user just visited the page (first)
        form = PageForm()
        return render(request, "encyclopedia/newpage.html", 
                      {'form': form})


def edit_page(request, page_title):
    """ Edit a page entry
    """
    page = util.get_entry(page_title)
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid:
            # if form is valid update entry
            p_content = request.POST['content']
            util.save_entry(page_title, p_content)  # save entry to disk
            content = markdown.markdown(p_content)
            return render(request, "encyclopedia/content.html", {
                "content": content,
                "title": page_title
                })
        else:
            messages.error(request, 'Form is invalid')
            return redirect('edit_page')
    else:  # user just visited the edit page
        initial_data = {'title': page_title,
                        'content': page}
        form = PageForm(initial=initial_data) # pre-populate form with page's data
        form.fields['title'].disabled = True # disable creating a new entry from edit page
        return render(request, "encyclopedia/edit.html",
                      {'form': form})


def random_page(request):
    """ Return a random page to the user every time called
    """
    pages = util.list_entries()
    rand_idx = random.randrange(len(pages))
    rand_page = pages[rand_idx]
    content = markdown.markdown(util.get_entry(rand_page))
    return render(request, "encyclopedia/content.html", {
        "content": content,
        "title": rand_page
        })
