"""Views for learning resources CRUD, filtering and pagination."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ActivityLog

from .forms import ResourceCategoryForm, ResourceForm
from .models import Resource, ResourceCategory

PAGE_SIZE = 10


@login_required
def resource_list(request):
    resources = Resource.objects.filter(user=request.user).prefetch_related(
        "categories"
    )

    resource_type = request.GET.get("type", "").strip()
    category_id = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()

    if resource_type in dict(Resource.ResourceType.choices):
        resources = resources.filter(resource_type=resource_type)
    if category_id.isdigit():
        resources = resources.filter(categories__id=int(category_id))
    if query:
        resources = resources.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    resources = resources.distinct()

    paginator = Paginator(resources, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "resources": page_obj.object_list,
        "categories": ResourceCategory.objects.filter(user=request.user),
        "type_choices": Resource.ResourceType.choices,
        "current_type": resource_type,
        "current_category": category_id,
        "query": query,
        "total_count": paginator.count,
    }
    return render(request, "resources/resource_list.html", context)


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    return render(request, "resources/resource_detail.html", {"resource": resource})


@login_required
def resource_create(request):
    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            resource = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.CREATED,
                "resource",
                f'Added resource "{resource.title}"',
                resource.pk,
            )
            messages.success(request, "Resource added successfully.")
            return redirect("resources:detail", pk=resource.pk)
    else:
        form = ResourceForm(user=request.user)
    return render(
        request,
        "resources/resource_form.html",
        {"form": form, "title": "Add Resource"},
    )


@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == "POST":
        form = ResourceForm(
            request.POST, request.FILES, instance=resource, user=request.user
        )
        if form.is_valid():
            resource = form.save()
            ActivityLog.log(
                request.user,
                ActivityLog.Action.UPDATED,
                "resource",
                f'Updated resource "{resource.title}"',
                resource.pk,
            )
            messages.success(request, "Resource updated successfully.")
            return redirect("resources:detail", pk=resource.pk)
    else:
        form = ResourceForm(instance=resource, user=request.user)
    return render(
        request,
        "resources/resource_form.html",
        {"form": form, "title": "Edit Resource", "resource": resource},
    )


@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == "POST":
        title = resource.title
        resource.delete()
        ActivityLog.log(
            request.user,
            ActivityLog.Action.DELETED,
            "resource",
            f'Deleted resource "{title}"',
        )
        messages.success(request, "Resource deleted.")
        return redirect("resources:list")
    return render(
        request, "resources/resource_confirm_delete.html", {"resource": resource}
    )


# --- Resource categories --------------------------------------------------
@login_required
def category_list(request):
    categories = ResourceCategory.objects.filter(user=request.user)
    if request.method == "POST":
        form = ResourceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category added.")
            return redirect("resources:category_list")
    else:
        form = ResourceCategoryForm()
    return render(
        request,
        "resources/category_list.html",
        {"categories": categories, "form": form},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(ResourceCategory, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("resources:category_list")
