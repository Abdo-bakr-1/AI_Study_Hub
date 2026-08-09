"""Views for notes CRUD, filtering, live-search and PDF export."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ActivityLog

from .forms import NoteCategoryForm, NoteForm
from .models import Note, NoteCategory
from .pdf import build_notes_pdf

PAGE_SIZE = 10


@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).prefetch_related("categories")

    category_id = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()

    if category_id.isdigit():
        notes = notes.filter(categories__id=int(category_id))
    if query:
        notes = notes.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    notes = notes.distinct()

    paginator = Paginator(notes, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "notes": page_obj.object_list,
        "categories": NoteCategory.objects.filter(user=request.user),
        "current_category": category_id,
        "query": query,
        "total_count": paginator.count,
    }
    return render(request, "notes/note_list.html", context)


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, "notes/note_detail.html", {"note": note})


@login_required
def note_create(request):
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            note = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.CREATED,
                "note",
                f'Created note "{note.title}"',
                note.pk,
            )
            messages.success(request, "Note created successfully.")
            return redirect("notes:detail", pk=note.pk)
    else:
        form = NoteForm(user=request.user)
    return render(
        request, "notes/note_form.html", {"form": form, "title": "Add Note"}
    )


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note, user=request.user)
        if form.is_valid():
            note = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.UPDATED,
                "note",
                f'Updated note "{note.title}"',
                note.pk,
            )
            messages.success(request, "Note updated successfully.")
            return redirect("notes:detail", pk=note.pk)
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(
        request,
        "notes/note_form.html",
        {"form": form, "title": "Edit Note", "note": note},
    )


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        title = note.title
        note.delete()
        ActivityLog.log(
            request.user,
            ActivityLog.Action.DELETED,
            "note",
            f'Deleted note "{title}"',
        )
        messages.success(request, "Note deleted.")
        return redirect("notes:list")
    return render(request, "notes/note_confirm_delete.html", {"note": note})


@login_required
def export_notes_pdf(request):
    """Export all of the current user's notes as a PDF."""
    notes = Note.objects.filter(user=request.user).prefetch_related("categories")
    return build_notes_pdf(request.user, notes)


# --- Note categories ------------------------------------------------------
@login_required
def category_list(request):
    categories = NoteCategory.objects.filter(user=request.user)
    if request.method == "POST":
        form = NoteCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category added.")
            return redirect("notes:category_list")
    else:
        form = NoteCategoryForm()
    return render(
        request,
        "notes/category_list.html",
        {"categories": categories, "form": form},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(NoteCategory, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("notes:category_list")
