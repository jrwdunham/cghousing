from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.http import Http404
from django.views import generic
from coop.models import Forum

# Co-op Home Page
def index(request):
    return HttpResponse("Welcome to the Co-op main page.")

# View all forums
class ForumsView(generic.ListView):
    model = Forum
    template_name = 'coop/forums.html'
    def get_queryset(self):
        return Forum.objects.all()

# View a forum
class ForumView(generic.DetailView):
    model = Forum
    template_name = 'coop/forum.html'

# View a forum after creation
class ForumResultsView(generic.DetailView):
    model = Forum
    template_name = 'coop/results.html'

# View a forum
def forum_(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    return render(request, 'coop/forum.html', {'forum': forum})

# Display page for creating a new forum.
def forum_new(request):
    return render(request, 'coop/forum_new.html')

# Save a forum using POST data.
def forum_save_(request):
    print request.POST
    return HttpResponse("You want to create a new forum.")

def forum_save(request):
    try:
        new_forum = Forum(
            name=request.POST['name'],
            description=request.POST['description'],
        )
        new_forum.save()
    except:
        # Redisplay the forum creation form.
        # TODO: put input data back in.
        return render(request, 'coop/forum_new.html', {
            'error_message': "There was an erorr: could not create forum."
        })
    else:
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('coop:forum_results', args=(new_forum.id,)))

