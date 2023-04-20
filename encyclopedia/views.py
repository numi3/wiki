from django.shortcuts import render, redirect
import markdown2, re
from django.urls import reverse
from django import forms
from . import util
import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })

def entry(request, entry):
    try:
        entry_content = markdown2.markdown(util.get_entry(entry))
    except:
        entry_content = "<h1>Error 404</h1> <p>Requested page was not found.</p>"

    return render(request, "encyclopedia/entry.html", {
        "entry_content": entry_content,
        "entry_title": entry,
    })

def search(request):
    if request.method == "POST":
        search = request.POST['q']
        results, count = find_entries(search)
        if count == 1:
            for entry_name in util.list_entries():
                if entry_name.lower() == search.lower():
                    return redirect(reverse('encyclopedia:entry', args=[search]))

        return render(request, "encyclopedia/search.html", {
            "search": search,
            "entries": results,
        })

def find_entries(search):
    results = []
    count = 0
    for entry in util.list_entries():
        if search.lower() in entry.lower():
            results.append(entry)
            count += 1
    return results, count

class NewEntryForm(forms.Form):
    title = forms.CharField(
        label="",
        max_length=32,
        min_length=3,
        widget=forms.TextInput(attrs={'placeholder': 'Enter title here', 'class': 'form-control'})
    )
    content = forms.CharField(
        label="",
        max_length=1000,
        min_length=10,
        widget=forms.Textarea(attrs={'cols': '50', 'rows': '4', 'class': 'form-control', 'placeholder': 'Enter content here'})
    )
    
def new(request):
    error_msg = False
    title = ""
    content = ""
    if request.method == "POST":
        title = request.POST["title"]
        form = NewEntryForm(request.POST)
        content = form.data['content'].encode('utf-8')
        if title.lower() not in [_entry.lower() for _entry in util.list_entries()]:
            util.save_entry(title, content)
            return redirect(reverse('encyclopedia:entry', args=[title]))
        else:
            error_msg = True
            content = request.POST['content']
    return render(request, "encyclopedia/new.html", {
        "error_msg": error_msg,
        "form": NewEntryForm(initial={
        'title': title,
        'content': content,
        }),
    })
            
def edit(request):
    if request.method == "POST":
        try:
            title = request.POST['entry_title']
            if title.lower() in [_entry.lower() for _entry in util.list_entries()]:
                content = util.get_entry(title)
                return render(request, "encyclopedia/edit.html", {
                    "edit_form": NewEntryForm(initial={'title': title, 'content': content}),
                    "original_title": title,
                })
        except KeyError:
            original_title = request.POST['original_title']
            title = request.POST['title']
            form = NewEntryForm(request.POST)
            content = form.data['content'].encode('utf-8')
            if title.lower() not in [_entry.lower() for _entry in util.list_entries() if _entry.lower() != original_title.lower()]:
                util.delete_entry(original_title)
                util.save_entry(title, content)
                return redirect(reverse('encyclopedia:entry', args=[title]))
            else:
                content = request.POST['content']
                return render(request, "encyclopedia/edit.html", {
                    "error_msg": True,
                    "edit_form": NewEntryForm(initial={
                        'title': title,
                        'content': content
                    }),
                    "original_title": original_title,
                })

def delete(request):
    if request.method == "POST":
        try:
            title = request.POST['entry_title']
            if title.lower() in [_entry.lower() for _entry in util.list_entries()]:
                util.delete_entry(title)
                return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries(),
                    "deleted_title": title,
                })
        except KeyError:
            pass
    return redirect(reverse('encyclopedia:index'))
        
        
def random_page(request):
    random_entry = random.choice(util.list_entries())
    return redirect(reverse('encyclopedia:entry', args=[random_entry]))