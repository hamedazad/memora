from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from datetime import datetime
import json

from .models import (
    Memory, UserProfile, FriendRequest, Friendship, Organization,
    OrganizationMembership, OrganizationInvitation, SharedMemory,
    MemoryComment, MemoryLike, Notification
)
from .forms import (
    UserProfileForm, FriendRequestForm, FindUserForm, OrganizationForm,
    OrganizationInvitationForm, DirectMemberAddForm, MemoryCommentForm, ShareMemoryForm
)


# User Profile Views

@login_required
def profile_view(request, username=None):
    """View user profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Check if viewing own profile
    is_own_profile = (user == request.user)
    
    # Check friendship status if not own profile
    friendship_status = None
    if not is_own_profile:
        if Friendship.are_friends(request.user, user):
            friendship_status = 'friends'
        elif FriendRequest.objects.filter(
            from_user=request.user, to_user=user, status='pending'
        ).exists():
            friendship_status = 'request_sent'
        elif FriendRequest.objects.filter(
            from_user=user, to_user=request.user, status='pending'
        ).exists():
            friendship_status = 'request_received'
    
    # Get user's public/shared memories
    if is_own_profile:
        memories = Memory.objects.filter(user=user, is_archived=False)
    else:
        memories = Memory.objects.filter(
            user=user, 
            is_archived=False
        ).filter(
            Q(privacy_level='public') |
            Q(privacy_level='friends', user__in=Friendship.get_user_friends(request.user)) |
            Q(shares__shared_with_user=request.user, shares__is_active=True)
        ).distinct()
    
    # Get recent memories
    recent_memories = memories.order_by('-created_at')[:5]
    
    # Get user's organizations
    organizations = user.organization_memberships.filter(is_active=True).select_related('organization')
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'friendship_status': friendship_status,
        'recent_memories': recent_memories,
        'organizations': organizations,
        'memories_count': memories.count(),
    }
    
    return render(request, 'memory_assistant/social/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('memory_assistant:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'memory_assistant/social/edit_profile.html', context)


# Friend Request Views

@login_required
def friends_list(request):
    """List user's friends"""
    friends = Friendship.get_user_friends(request.user)
    
    # Paginate friends
    paginator = Paginator(friends, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get pending friend requests (received)
    pending_requests = FriendRequest.objects.filter(
        to_user=request.user, status='pending'
    ).order_by('-created_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'friends': friends,
        'friends_count': len(friends),
        'pending_requests': pending_requests,
        'pending_count': pending_requests.count(),
    }
    
    return render(request, 'memory_assistant/social/friends_list.html', context)


@login_required
def find_users(request):
    """Find users to send friend requests"""
    form = FindUserForm()
    users = []
    
    if request.method == 'GET' and 'query' in request.GET:
        form = FindUserForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(id=request.user.id)[:20]
            
            # Add friendship status for each user
            for user in users:
                if Friendship.are_friends(request.user, user):
                    user.friendship_status = 'friends'
                elif FriendRequest.objects.filter(
                    from_user=request.user, to_user=user, status='pending'
                ).exists():
                    user.friendship_status = 'request_sent'
                elif FriendRequest.objects.filter(
                    from_user=user, to_user=request.user, status='pending'
                ).exists():
                    user.friendship_status = 'request_received'
                else:
                    user.friendship_status = 'none'
    
    context = {
        'form': form,
        'users': users,
    }
    
    return render(request, 'memory_assistant/social/find_users.html', context)


@login_required
@require_POST
def send_friend_request(request, user_id):
    """Send friend request to user"""
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect('memory_assistant:find_users')
    
    # Check if already friends
    if Friendship.are_friends(request.user, to_user):
        messages.info(request, f"You are already friends with {to_user.username}.")
        return redirect('memory_assistant:profile', username=to_user.username)
    
    # Check if request already exists
    existing_request = FriendRequest.objects.filter(
        from_user=request.user, to_user=to_user, status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, f"Friend request already sent to {to_user.username}.")
        return redirect('memory_assistant:profile', username=to_user.username)
    
    # Create friend request
    message = request.POST.get('message', '')
    friend_request = FriendRequest.objects.create(
        from_user=request.user,
        to_user=to_user,
        message=message
    )
    
    # Create notification
    Notification.objects.create(
        recipient=to_user,
        sender=request.user,
        notification_type='friend_request',
        title='New Friend Request',
        message=f'{request.user.username} sent you a friend request.',
        related_object_id=friend_request.id,
        related_object_type='friend_request',
        action_url=f'/memora/social/friends/requests/'
    )
    
    messages.success(request, f'Friend request sent to {to_user.username}!')
    return redirect('memory_assistant:profile', username=to_user.username)


@login_required
def friend_requests(request):
    """View received friend requests"""
    received_requests = FriendRequest.objects.filter(
        to_user=request.user, status='pending'
    ).order_by('-created_at')
    
    sent_requests = FriendRequest.objects.filter(
        from_user=request.user, status='pending'
    ).order_by('-created_at')
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    
    return render(request, 'memory_assistant/social/friend_requests.html', context)


@login_required
@require_POST
def respond_friend_request(request, request_id):
    """Accept or decline friend request"""
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user, status='pending'
    )
    
    action = request.POST.get('action')
    
    with transaction.atomic():
        if action == 'accept':
            # Create friendship
            Friendship.objects.create(
                user1=friend_request.from_user,
                user2=friend_request.to_user
            )
            
            # Update request status
            friend_request.status = 'accepted'
            friend_request.responded_at = timezone.now()
            friend_request.save()
            
            # Create notification
            Notification.objects.create(
                recipient=friend_request.from_user,
                sender=request.user,
                notification_type='friend_accepted',
                title='Friend Request Accepted',
                message=f'{request.user.username} accepted your friend request!',
                action_url=f'/memora/social/profile/{request.user.username}/'
            )
            
            messages.success(request, f'You are now friends with {friend_request.from_user.username}!')
            
        elif action == 'decline':
            friend_request.status = 'declined'
            friend_request.responded_at = timezone.now()
            friend_request.save()
            
            messages.info(request, 'Friend request declined.')
    
    return redirect('memory_assistant:friend_requests')


# Organization Views

@login_required
def organizations_list(request):
    """List user's organizations"""
    user_memberships = request.user.organization_memberships.filter(
        is_active=True
    ).select_related('organization').order_by('organization__name')
    
    # Get organizations user can discover (public ones)
    public_orgs = Organization.objects.filter(
        privacy='public', is_active=True
    ).exclude(
        id__in=user_memberships.values_list('organization_id', flat=True)
    ).order_by('name')[:10]
    
    context = {
        'user_memberships': user_memberships,
        'public_orgs': public_orgs,
    }
    
    return render(request, 'memory_assistant/social/organizations_list.html', context)


@login_required
def organization_detail(request, org_id):
    """View organization details"""
    organization = get_object_or_404(Organization, id=org_id, is_active=True)
    
    # Check if user is member
    membership = OrganizationMembership.objects.filter(
        organization=organization, user=request.user, is_active=True
    ).first()
    
    is_member = bool(membership)
    
    # Get organization members (if user is member or org is public)
    if is_member or organization.privacy == 'public':
        members = organization.memberships.filter(is_active=True).select_related('user')
        
        # Get shared memories in this organization
        org_memories = SharedMemory.objects.filter(
            shared_with_organization=organization,
            is_active=True
        ).select_related('memory', 'shared_by').order_by('-created_at')[:10]
    else:
        members = None
        org_memories = None
    
    context = {
        'organization': organization,
        'membership': membership,
        'is_member': is_member,
        'members': members,
        'org_memories': org_memories,
    }
    
    return render(request, 'memory_assistant/social/organization_detail.html', context)


@login_required
def create_organization(request):
    """Create new organization"""
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.created_by = request.user
            organization.save()
            
            # Create admin membership for creator
            OrganizationMembership.objects.create(
                organization=organization,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, f'Organization "{organization.name}" created successfully!')
            return redirect('memory_assistant:organization_detail', org_id=organization.id)
    else:
        form = OrganizationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'memory_assistant/social/create_organization.html', context)


# Memory Sharing Views

@login_required
def share_memory(request, memory_id):
    """Share memory with friends or organizations"""
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)
    
    if request.method == 'POST':
        form = ShareMemoryForm(request.user, request.POST)
        if form.is_valid():
            share_type = form.cleaned_data['share_type']
            message = form.cleaned_data['message']
            can_reshare = form.cleaned_data['can_reshare']
            
            if share_type == 'user':
                recipient_user = form.cleaned_data['recipient_user']
                shared_memory = SharedMemory.objects.create(
                    memory=memory,
                    shared_by=request.user,
                    shared_with_user=recipient_user,
                    share_type='user',
                    message=message,
                    can_reshare=can_reshare
                )
                
                # Create notification
                Notification.objects.create(
                    recipient=recipient_user,
                    sender=request.user,
                    notification_type='memory_shared',
                    title='Memory Shared With You',
                    message=f'{request.user.username} shared a memory with you.',
                    related_object_id=memory.id,
                    related_object_type='memory',
                    action_url=f'/memora/memories/{memory.id}/'
                )
                
                messages.success(request, f'Memory shared with {recipient_user.username}!')
                
            elif share_type == 'organization':
                recipient_org = form.cleaned_data['recipient_organization']
                shared_memory = SharedMemory.objects.create(
                    memory=memory,
                    shared_by=request.user,
                    shared_with_organization=recipient_org,
                    share_type='organization',
                    message=message,
                    can_reshare=can_reshare
                )
                
                messages.success(request, f'Memory shared with {recipient_org.name}!')
            
            # Update memory shared count
            memory.shared_count += 1
            memory.save()
            
            return redirect('memory_assistant:memory_detail', memory_id=memory.id)
    else:
        form = ShareMemoryForm(request.user)
    
    context = {
        'form': form,
        'memory': memory,
    }
    
    return render(request, 'memory_assistant/social/share_memory.html', context)


@login_required
def shared_with_me(request):
    """View memories shared with current user"""
    # Memories shared directly with user
    user_shares = SharedMemory.objects.filter(
        shared_with_user=request.user,
        is_active=True
    ).select_related('memory', 'shared_by').prefetch_related(
        'memory__comments__user__profile',
        'memory__likes__user'
    ).order_by('-created_at')
    
    # Memories shared with user's organizations
    user_orgs = request.user.organization_memberships.filter(
        is_active=True
    ).values_list('organization', flat=True)
    
    org_shares = SharedMemory.objects.filter(
        shared_with_organization__in=user_orgs,
        is_active=True
    ).select_related('memory', 'shared_by', 'shared_with_organization').prefetch_related(
        'memory__comments__user__profile',
        'memory__likes__user'
    ).order_by('-created_at')
    
    # Combine and paginate
    all_shares = list(user_shares) + list(org_shares)
    all_shares.sort(key=lambda x: x.created_at, reverse=True)
    
    paginator = Paginator(all_shares, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'memory_assistant/social/shared_with_me.html', context)


# Memory Interaction Views

@login_required
@require_POST
def add_comment(request, memory_id):
    """Add comment to memory"""
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Check if user can view this memory
    if not memory.can_be_viewed_by(request.user):
        messages.error(request, "You don't have permission to comment on this memory.")
        return redirect('memory_assistant:dashboard')
    
    # Check if comments are allowed
    if not memory.allow_comments:
        messages.error(request, "Comments are not allowed on this memory.")
        return redirect('memory_assistant:memory_detail', memory_id=memory.id)
    
    form = MemoryCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.memory = memory
        comment.user = request.user
        comment.save()
        
        # Create notification for memory owner (if not commenting on own memory)
        if memory.user != request.user:
            Notification.objects.create(
                recipient=memory.user,
                sender=request.user,
                notification_type='memory_comment',
                title='New Comment on Your Memory',
                message=f'{request.user.username} commented on your memory.',
                related_object_id=memory.id,
                related_object_type='memory',
                action_url=f'/memora/memories/{memory.id}/'
            )
        
        messages.success(request, 'Comment added successfully!')
    
    return redirect('memory_assistant:memory_detail', memory_id=memory.id)


@login_required
@require_POST
def toggle_like(request, memory_id):
    """Toggle like/reaction on memory"""
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Check if user can view this memory
    if not memory.can_be_viewed_by(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Check if likes are allowed
    if not memory.allow_likes:
        return JsonResponse({'error': 'Likes not allowed on this memory'}, status=400)
    
    reaction_type = request.POST.get('reaction_type', 'like')
    
    # Get or create like
    like, created = MemoryLike.objects.get_or_create(
        memory=memory,
        user=request.user,
        defaults={'reaction_type': reaction_type}
    )
    
    if not created:
        if like.reaction_type == reaction_type:
            # Remove like if same reaction
            like.delete()
            liked = False
        else:
            # Update reaction type
            like.reaction_type = reaction_type
            like.save()
            liked = True
    else:
        liked = True
        
        # Create notification for memory owner (if not liking own memory)
        if memory.user != request.user:
            Notification.objects.create(
                recipient=memory.user,
                sender=request.user,
                notification_type='memory_like',
                title='Someone Liked Your Memory',
                message=f'{request.user.username} reacted to your memory.',
                related_object_id=memory.id,
                related_object_type='memory',
                action_url=f'/memora/memories/{memory.id}/'
            )
    
    return JsonResponse({
        'liked': liked,
        'likes_count': memory.get_likes_count(),
        'user_reaction': memory.get_user_reaction(request.user)
    })


# Notification Views

@login_required
def notifications(request):
    """View user notifications"""
    notifications = request.user.notifications.order_by('-created_at')
    
    # Mark all as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    # Get invitation statuses for organization invitation notifications
    invitation_statuses = {}
    org_invitation_notifications = notifications.filter(notification_type='organization_invitation')
    for notification in org_invitation_notifications:
        try:
            invitation = OrganizationInvitation.objects.get(id=notification.related_object_id)
            invitation_statuses[notification.id] = invitation.status
        except OrganizationInvitation.DoesNotExist:
            invitation_statuses[notification.id] = 'deleted'
    
    # Paginate
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'invitation_statuses': invitation_statuses,
    }
    
    return render(request, 'memory_assistant/social/notifications.html', context)


@login_required
def notifications_count(request):
    """Get unread notifications count (for AJAX)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


# Organization Member Management Views

@login_required
def organization_members(request, org_id):
    """View and manage organization members"""
    organization = get_object_or_404(Organization, id=org_id, is_active=True)
    
    # Check if user has permission to view members
    membership = OrganizationMembership.objects.filter(
        organization=organization, user=request.user, is_active=True
    ).first()
    
    if not membership:
        messages.error(request, 'You are not a member of this organization.')
        return redirect('memory_assistant:organizations_list')
    
    # Get all organization members
    members = OrganizationMembership.objects.filter(
        organization=organization, is_active=True
    ).select_related('user').order_by('-joined_at')
    
    # Get pending invitations
    pending_invitations = OrganizationInvitation.objects.filter(
        organization=organization, status='pending'
    ).select_related('to_user', 'from_user').order_by('-created_at')
    
    # Check if user can manage members (admin or moderator)
    can_manage = membership.role in ['admin', 'moderator']
    is_admin = membership.role == 'admin'
    
    context = {
        'organization': organization,
        'members': members,
        'pending_invitations': pending_invitations,
        'user_membership': membership,
        'can_manage': can_manage,
        'is_admin': is_admin,
    }
    
    return render(request, 'memory_assistant/social/organization_members.html', context)


@login_required
def invite_organization_member(request, org_id):
    """Invite a user to join the organization"""
    organization = get_object_or_404(Organization, id=org_id, is_active=True)
    
    # Check if user has permission to invite members
    membership = OrganizationMembership.objects.filter(
        organization=organization, user=request.user, is_active=True
    ).first()
    
    if not membership or membership.role not in ['admin', 'moderator']:
        messages.error(request, 'You do not have permission to invite members.')
        return redirect('memory_assistant:organization_members', org_id=org_id)
    
    if request.method == 'POST':
        form = OrganizationInvitationForm(request.POST)
        if form.is_valid():
            try:
                invite_user = form.cleaned_data['invite_username']
                
                # Check if user is already a member
                existing_membership = OrganizationMembership.objects.filter(
                    organization=organization, user=invite_user, is_active=True
                ).exists()
                
                if existing_membership:
                    messages.error(request, f'{invite_user.username} is already a member of this organization.')
                    return redirect('memory_assistant:organization_members', org_id=org_id)
                
                # Check if invitation already exists (any status)
                existing_invitation = OrganizationInvitation.objects.filter(
                    organization=organization, to_user=invite_user
                ).first()
                
                if existing_invitation:
                    if existing_invitation.status == 'pending':
                        messages.error(request, f'A pending invitation has already been sent to {invite_user.username}.')
                        return redirect('memory_assistant:organization_members', org_id=org_id)
                    elif existing_invitation.status == 'accepted':
                        # Check if they're actually still an active member
                        is_still_member = OrganizationMembership.objects.filter(
                            organization=organization, user=invite_user, is_active=True
                        ).exists()
                        
                        if is_still_member:
                            messages.error(request, f'{invite_user.username} is already a member of this organization.')
                            return redirect('memory_assistant:organization_members', org_id=org_id)
                        else:
                            # User was removed but invitation still shows "accepted"
                            # Allow re-invitation by updating the existing invitation
                            existing_invitation.status = 'pending'
                            existing_invitation.role = form.cleaned_data['role']
                            existing_invitation.message = form.cleaned_data.get('message', '')
                            existing_invitation.created_at = timezone.now()
                            existing_invitation.responded_at = None
                            existing_invitation.from_user = request.user
                            existing_invitation.save()
                            invitation = existing_invitation
                    elif existing_invitation.status == 'declined':
                        # Allow resending invitation to users who previously declined
                        # Update the existing invitation instead of creating a new one
                        existing_invitation.status = 'pending'
                        existing_invitation.role = form.cleaned_data['role']
                        existing_invitation.message = form.cleaned_data.get('message', '')
                        existing_invitation.created_at = timezone.now()
                        existing_invitation.responded_at = None
                        existing_invitation.from_user = request.user
                        existing_invitation.save()
                        invitation = existing_invitation
                    elif existing_invitation.status == 'cancelled':
                        # Allow resending invitation that was previously cancelled
                        existing_invitation.status = 'pending'
                        existing_invitation.role = form.cleaned_data['role']
                        existing_invitation.message = form.cleaned_data.get('message', '')
                        existing_invitation.created_at = timezone.now()
                        existing_invitation.responded_at = None
                        existing_invitation.from_user = request.user
                        existing_invitation.save()
                        invitation = existing_invitation
                else:
                    # Create new invitation
                    invitation = OrganizationInvitation.objects.create(
                        organization=organization,
                        from_user=request.user,
                        to_user=invite_user,
                        role=form.cleaned_data['role'],
                        message=form.cleaned_data.get('message', '')
                    )
                
                # Create notification
                Notification.objects.create(
                    recipient=invite_user,
                    sender=request.user,
                    notification_type='organization_invitation',
                    title=f'Organization Invitation: {organization.name}',
                    message=f'{request.user.get_full_name() or request.user.username} invited you to join {organization.name} as a {invitation.role}.',
                    related_object_id=invitation.id,
                    related_object_type='organization_invitation'
                )
                
                # Success message based on whether it's a new invitation or resent
                if existing_invitation:
                    messages.success(request, f'Invitation sent to {invite_user.username}!')
                else:
                    messages.success(request, f'Invitation sent to {invite_user.username}!')
                return redirect('memory_assistant:organization_members', org_id=org_id)
                
            except Exception as e:
                messages.error(request, f'Error sending invitation: {str(e)}')
    else:
        form = OrganizationInvitationForm()
    
    context = {
        'organization': organization,
        'form': form,
        'user_membership': membership,
    }
    
    return render(request, 'memory_assistant/social/invite_member.html', context)


@login_required
def add_organization_member_direct(request, org_id):
    """Directly add a member to organization (admin only)"""
    organization = get_object_or_404(Organization, id=org_id, is_active=True)
    
    # Check if user is admin
    membership = OrganizationMembership.objects.filter(
        organization=organization, user=request.user, is_active=True, role='admin'
    ).first()
    
    if not membership:
        messages.error(request, 'Only organization admins can directly add members.')
        return redirect('memory_assistant:organization_members', org_id=org_id)
    
    if request.method == 'POST':
        form = DirectMemberAddForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.cleaned_data['username']
                role = form.cleaned_data['role']
                
                # Check if user is already a member
                existing_membership = OrganizationMembership.objects.filter(
                    organization=organization, user=new_user, is_active=True
                ).exists()
                
                if existing_membership:
                    messages.error(request, f'{new_user.username} is already a member of this organization.')
                    return redirect('memory_assistant:organization_members', org_id=org_id)
                
                # Create membership
                with transaction.atomic():
                    OrganizationMembership.objects.create(
                        organization=organization,
                        user=new_user,
                        role=role,
                        is_active=True
                    )
                    
                    # Create notification
                    Notification.objects.create(
                        recipient=new_user,
                        sender=request.user,
                        notification_type='organization_added',
                        title=f'Added to Organization: {organization.name}',
                        message=f'You have been added to {organization.name} as a {role} by {request.user.get_full_name() or request.user.username}.',
                        related_object_id=organization.id,
                        related_object_type='organization'
                    )
                
                messages.success(request, f'{new_user.username} has been added as a {role}!')
                return redirect('memory_assistant:organization_members', org_id=org_id)
                
            except Exception as e:
                messages.error(request, f'Error adding member: {str(e)}')
    else:
        form = DirectMemberAddForm()
    
    context = {
        'organization': organization,
        'form': form,
        'user_membership': membership,
    }
    
    return render(request, 'memory_assistant/social/add_member_direct.html', context)


@login_required
def remove_organization_member(request, org_id, member_id):
    """Remove a member from the organization"""
    organization = get_object_or_404(Organization, id=org_id, is_active=True)
    member_to_remove = get_object_or_404(User, id=member_id)
    
    # Check if user has permission to remove members
    user_membership = OrganizationMembership.objects.filter(
        organization=organization, user=request.user, is_active=True
    ).first()
    
    member_membership = OrganizationMembership.objects.filter(
        organization=organization, user=member_to_remove, is_active=True
    ).first()
    
    if not user_membership:
        messages.error(request, 'You are not a member of this organization.')
        return redirect('memory_assistant:organizations_list')
    
    if not member_membership:
        messages.error(request, 'User is not a member of this organization.')
        return redirect('memory_assistant:organization_members', org_id=org_id)
    
    # Permission check
    can_remove = False
    if user_membership.role == 'admin':
        # Admins can remove anyone except other admins (unless it's themselves)
        if member_membership.role != 'admin' or member_to_remove == request.user:
            can_remove = True
    elif user_membership.role == 'moderator' and member_membership.role in ['member', 'viewer']:
        # Moderators can remove members and viewers
        can_remove = True
    elif member_to_remove == request.user:
        # Users can always remove themselves
        can_remove = True
    
    if not can_remove:
        messages.error(request, 'You do not have permission to remove this member.')
        return redirect('memory_assistant:organization_members', org_id=org_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Mark membership as inactive instead of deleting
                member_membership.is_active = False
                member_membership.save()
                
                # Update invitation status to allow re-invitation
                # Find the accepted invitation for this user and organization
                accepted_invitation = OrganizationInvitation.objects.filter(
                    organization=organization,
                    to_user=member_to_remove,
                    status='accepted'
                ).first()
                
                if accepted_invitation:
                    # Mark invitation as cancelled to allow re-invitation
                    accepted_invitation.status = 'cancelled'
                    accepted_invitation.save()
                
                # Create notification (if not removing themselves)
                if member_to_remove != request.user:
                    Notification.objects.create(
                        recipient=member_to_remove,
                        sender=request.user,
                        notification_type='organization_removed',
                        title=f'Removed from Organization: {organization.name}',
                        message=f'You have been removed from {organization.name} by {request.user.get_full_name() or request.user.username}.',
                        related_object_id=organization.id,
                        related_object_type='organization'
                    )
            
            if member_to_remove == request.user:
                messages.success(request, 'You have left the organization.')
                return redirect('memory_assistant:organizations_list')
            else:
                messages.success(request, f'{member_to_remove.username} has been removed from the organization.')
                return redirect('memory_assistant:organization_members', org_id=org_id)
                
        except Exception as e:
            messages.error(request, f'Error removing member: {str(e)}')
    
    context = {
        'organization': organization,
        'member_to_remove': member_to_remove,
        'member_membership': member_membership,
        'user_membership': user_membership,
    }
    
    return render(request, 'memory_assistant/social/remove_member.html', context)


# Organization Invitation Response Views

@login_required
def respond_organization_invitation(request, invitation_id):
    """Accept or decline organization invitation"""
    # First get the invitation without status filter
    invitation = get_object_or_404(
        OrganizationInvitation, 
        id=invitation_id, 
        to_user=request.user
    )
    
    # Check if invitation is still pending
    if invitation.status != 'pending':
        if invitation.status == 'accepted':
            messages.info(request, f'You have already accepted the invitation to join {invitation.organization.name}.')
            return redirect('memory_assistant:organization_detail', org_id=invitation.organization.id)
        elif invitation.status == 'declined':
            messages.info(request, f'You have already declined the invitation to join {invitation.organization.name}.')
        else:
            messages.info(request, 'This invitation is no longer active.')
        return redirect('memory_assistant:notifications')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        with transaction.atomic():
            if action == 'accept':
                # Check if user is already a member
                existing_membership = OrganizationMembership.objects.filter(
                    organization=invitation.organization,
                    user=request.user
                ).first()
                
                if existing_membership:
                    if existing_membership.is_active:
                        # User is already an active member
                        messages.info(request, f'You are already a member of {invitation.organization.name}.')
                        invitation.status = 'accepted'
                        invitation.responded_at = timezone.now()
                        invitation.save()
                        return redirect('memory_assistant:organization_detail', org_id=invitation.organization.id)
                    else:
                        # Reactivate existing membership with new role
                        existing_membership.role = invitation.role
                        existing_membership.is_active = True
                        existing_membership.joined_at = timezone.now()
                        existing_membership.save()
                else:
                    # Create new organization membership
                    OrganizationMembership.objects.create(
                        organization=invitation.organization,
                        user=request.user,
                        role=invitation.role,
                        is_active=True
                    )
                
                # Update invitation status
                invitation.status = 'accepted'
                invitation.responded_at = timezone.now()
                invitation.save()
                
                # Create notification for inviter
                Notification.objects.create(
                    recipient=invitation.from_user,
                    sender=request.user,
                    notification_type='organization_joined',
                    title=f'Invitation Accepted: {invitation.organization.name}',
                    message=f'{request.user.get_full_name() or request.user.username} joined {invitation.organization.name}!',
                    related_object_id=invitation.organization.id,
                    related_object_type='organization'
                )
                
                messages.success(request, f'Welcome to {invitation.organization.name}! You are now a {invitation.role}.')
                return redirect('memory_assistant:organization_detail', org_id=invitation.organization.id)
                
            elif action == 'decline':
                # Update invitation status
                invitation.status = 'declined'
                invitation.responded_at = timezone.now()
                invitation.save()
                
                messages.info(request, f'You declined the invitation to join {invitation.organization.name}.')
                return redirect('memory_assistant:notifications')
    
    context = {
        'invitation': invitation,
    }
    
    return render(request, 'memory_assistant/social/respond_invitation.html', context)


@login_required
def my_organization_invitations(request):
    """View user's pending organization invitations"""
    pending_invitations = OrganizationInvitation.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('organization', 'from_user').order_by('-created_at')
    
    context = {
        'pending_invitations': pending_invitations,
    }
    
    return render(request, 'memory_assistant/social/my_invitations.html', context)
