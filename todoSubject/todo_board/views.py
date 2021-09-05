from django.shortcuts import render, redirect
from .models import TodoList
from .forms import TodoForm
from django.views import View
from django.views import generic
from django.http import JsonResponse
from datetime import datetime, timedelta
import simplejson as json

# Create your views here.
class Todo_board(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        #Reserved.objects.filter(client=client_id).order_by('-check_in')
        template_name = 'todo_board/todo_list.html'
        #기한 없는 일정, 마감 안된 애들
        todo_list_no_endDate = TodoList.objects.all().filter(end_date__isnull=True, is_complete=0).order_by('priority')
        #기한 있고, 마감이 안된 애들
        todo_list_endDate_non_complete = TodoList.objects.all().filter(end_date__isnull=False, is_complete=0).order_by('priority')
        #마감이 된 애들
        todo_list_endDate_complete = TodoList.objects.all().filter(is_complete=1).order_by('end_date')
        today = datetime.now()
        #마감임박
        close_end_day = []
        #마감지남
        over_end_day = []
        for i in todo_list_endDate_non_complete:
            e_day = str(i.end_date).split("-")
            end_day = datetime(int(e_day[0]), int(e_day[1]), int(e_day[2]))
            if (end_day - today).days < -1: over_end_day.append(i.title)
            if (end_day - today).days >= -1 and (end_day - today).days < 3: close_end_day.append(i.title)
        return render(request, template_name, {"todo_list_endDate_non_complete": todo_list_endDate_non_complete, "todo_list_endDate_complete": todo_list_endDate_complete, "todo_list_no_endDate": todo_list_no_endDate, 'close_end_day': close_end_day, 'over_end_day':over_end_day})

class Todo_board_detail(generic.DetailView):
    model = TodoList
    template_name = 'todo_board/todo_board_detail.html'
    context_object_name = 'todo_list'

class Todo_board_update(generic.UpdateView):
    model = TodoList
    template_name = 'todo_board/todo_board_update.html'
    fields = ('title', 'content', 'end_date')
    success_url = '/board/'

    def form_valid(self, form):
        form.save()
        return render(self.request, 'todo_board/todo_board_success.html', {"message": "일정을 업데이트 했습니다"})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)

class Todo_board_delete(generic.DeleteView):
    model = TodoList
    success_url = '/board/'
    context_object_name = 'todo_list'

def checkbox_event(pk, is_check):
    todo_selected = TodoList.objects.get(pk=pk)
    if is_check == True:
        todo_selected.is_complete = 1
        todo_selected.priority = None
    else:
        todo_selected.is_complete = 0
    todo_selected.save()
    return_value = {'text': '저장되었습니다.'}
    return return_value

def check_post(request):
    template_name = 'todo_board/todo_board_success.html'
    if request.method == "POST":
        form = TodoForm(request.POST)
        if str(request.path).split("/board/")[1].split("/")[0] == "insert":
            if form.is_valid():
                todo = form.save(commit=False)
                todo.todo_save()
                message = "일정을 추가하였습니다. "
                return render(request, template_name, {"message": message})
        elif str(request.path).split("/board/")[1].split("/")[0] == "is_complete":
            pk = request.POST['data']
            return_value = checkbox_event(pk, True)
            return JsonResponse(return_value)
        elif str(request.path).split("/board/")[1].split("/")[0] == "is_non_complete":
            pk = request.POST['data']
            return_value = checkbox_event(pk, False)
            return JsonResponse(return_value)
        else:
            template_name = 'todo_board/todo_board_insert.html'
            form = TodoForm
            return render(request, template_name, {"form": form})