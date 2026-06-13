from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.db import transaction
from .models import Game, GameCategoryAllocation, Status, SpeedrunType, Speedrun
from .forms import AcceptGameRequestFormSet, AcceptSpeedrunTypeRequestFormSet, AcceptSpeedrunRequestFormSet



@admin.action(description="Reject Request")
def reject_request(modeladmin, request, queryset):
    updated = queryset.update(status=Status.REJECTED)
    modeladmin.message_user(
        request, 
        f'Successfully rejected {updated} request(s).', 
        messages.SUCCESS
    )


@admin.action(description="Process Game Requests (Accept or Reject)")
def accept_and_configure_game(modeladmin, request, queryset):
    if 'apply' in request.POST:
        formset = AcceptGameRequestFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            accepted_count = 0
            rejected_count = 0
            
            with transaction.atomic():
                for form in formset:
                    req_id = form.cleaned_data.get('request_id')
                    is_rejected = form.cleaned_data.get('reject')
                    
                    game_req = modeladmin.model.objects.filter(id=req_id).first()
                    if not game_req:
                        continue
                    
                    if is_rejected:
                        # Process Rejection
                        game_req.status = Status.REJECTED
                        game_req.save()
                        rejected_count += 1
                    else:
                        # Process Acceptance
                        uploaded_image = form.cleaned_data.get('cover_image')
                        selected_categories = form.cleaned_data.get('categories')
                        final_title = form.cleaned_data.get('game_title')
                        description = form.cleaned_data.get('description')
                        
                        # Create the Game
                        game = Game.objects.create(
                            name=final_title, 
                            release_date=game_req.release_date,
                            description=description,
                            image=uploaded_image 
                        )
                        
                        # Create the Category Allocations
                        allocations = [
                            GameCategoryAllocation(game=game, category=category)
                            for category in selected_categories
                        ]
                        GameCategoryAllocation.objects.bulk_create(allocations)
                        
                        # Update status
                        game_req.status = Status.ACCEPTED
                        game_req.save()
                        accepted_count += 1
                    
            msg = f"Processing complete. Accepted {accepted_count} game(s)"
            if rejected_count:
                msg += f" and rejected {rejected_count} request(s)"
            msg += "."
            
            modeladmin.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(request.get_full_path())
        else:
            modeladmin.message_user(request, "Please correct the errors below.", messages.ERROR)

    else:
        # Pre-fill
        initial_data = [
            {
                'request_id': req.id,
                'game_title': req.title,
            }
            for req in queryset
        ]
        formset = AcceptGameRequestFormSet(initial=initial_data)

    opts = modeladmin.model._meta

    return render(
        request,
        'admin/accept_game_request.html',
        context={
            'items': queryset, 
            'formset': formset,
            'title': 'Configure Game Details',
            'opts': opts
        }
    )

@admin.action(description="Process Speedrun Type Requests (Accept or Reject)")
def accept_and_configure_speedrun_type(modeladmin, request, queryset):
    if 'apply' in request.POST:
        formset = AcceptSpeedrunTypeRequestFormSet(request.POST)
        
        if formset.is_valid():
            accepted_count = 0
            rejected_count = 0
            
            with transaction.atomic():
                for form in formset:
                    req_id = form.cleaned_data.get('request_id')
                    is_rejected = form.cleaned_data.get('reject')
                    
                    req_obj = modeladmin.model.objects.filter(id=req_id).first()
                    if not req_obj:
                        continue
                    
                    if is_rejected:
                        req_obj.status = Status.REJECTED
                        req_obj.save()
                        rejected_count += 1
                    else:
                        final_name = form.cleaned_data.get('name')
                        description = form.cleaned_data.get('description')
                        assigned_game = form.cleaned_data.get('game')
                        
                        SpeedrunType.objects.create(
                            name=final_name,
                            description=description,
                            game=assigned_game
                        )
                        
                        req_obj.status = Status.ACCEPTED
                        req_obj.save()
                        accepted_count += 1
                    
            msg = f"Processing complete. Accepted {accepted_count} speedrun type(s)"
            if rejected_count:
                msg += f" and rejected {rejected_count} request(s)"
            msg += "."
            
            modeladmin.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(request.get_full_path())
        else:
            modeladmin.message_user(request, "Please correct the errors below.", messages.ERROR)
    else:
        initial_data = [
            {
                'request_id': req.id,
                'url': req.url,
                'time': req.time,
                'date': req.date,
                'speedrun_type': req.speedrun_type if req.speedrun_type else None,
                'username': req.user.username if req.user else "Unknown",
            }
            for req in queryset
        ]
        formset = AcceptSpeedrunRequestFormSet(initial=initial_data)

    opts = modeladmin.model._meta

    return render(
        request,
        'admin/accept_speedrun_type_request.html',
        context={
            'items': queryset, 
            'formset': formset,
            'title': 'Configure Speedrun Type Details',
            'opts': opts
        }
    )
    

@admin.action(description="Process Speedrun Requests (Accept or Reject)")
def accept_and_configure_speedrun(modeladmin, request, queryset):
    if 'apply' in request.POST:
        formset = AcceptSpeedrunRequestFormSet(request.POST)
        
        if formset.is_valid():
            accepted_count = 0
            rejected_count = 0
            
            with transaction.atomic():
                for form in formset:
                    req_id = form.cleaned_data.get('request_id')
                    is_rejected = form.cleaned_data.get('reject')
                    
                    req_obj = modeladmin.model.objects.filter(id=req_id).first()
                    if not req_obj:
                        continue
                    
                    if is_rejected:
                        req_obj.status = Status.REJECTED
                        req_obj.save()
                        rejected_count += 1
                    else:
                        req_obj.url = form.cleaned_data.get('url')
                        req_obj.time = form.cleaned_data.get('time')
                        req_obj.date = form.cleaned_data.get('date')
                        req_obj.speedrun_type = form.cleaned_data.get('speedrun_type')
                        req_obj.status = Status.ACCEPTED
                        req_obj.save()
                        
                        accepted_count += 1
                    
            msg = f"Processing complete. Accepted {accepted_count} speedrun(s)"
            if rejected_count:
                msg += f" and rejected {rejected_count} request(s)"
            msg += "."
            
            modeladmin.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(request.get_full_path())
        else:
            modeladmin.message_user(request, "Please correct the errors below.", messages.ERROR)
    else:
        initial_data = [
            {
                'request_id': req.id,
                'url': req.url,
                'time': req.time,
                'date': req.date,
                'speedrun_type': req.speedrun_type if req.speedrun_type else None,
                'username': req.user.username if req.user else "Unknown",
            }
            for req in queryset
        ]
        formset = AcceptSpeedrunRequestFormSet(initial=initial_data)

    opts = modeladmin.model._meta

    return render(
        request,
        'admin/accept_speedrun_request.html',
        context={
            'items': queryset, 
            'formset': formset,
            'title': 'Configure Speedrun Details',
            'opts': opts
        }
    )