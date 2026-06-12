from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.db import transaction
from .models import Game, GameCategoryAllocation, Status
from .forms import AcceptGameRequestFormSet


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