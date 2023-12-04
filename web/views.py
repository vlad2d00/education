from django.contrib.auth import logout as django_logout, login as django_login, authenticate
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from api.db.dao import *
from api.signals import get_model_or_none
from education.utils.datetime_service import datetime_now, subtract_datetime
from web.forms import *
from web.utils.exceptions import PageNotFoundException, PermissionDeniedException
from web.utils.navigation import NavigationItemTitle
from web.utils.web_view import web_view


def get_page_number(request, name: str = None) -> int:
    page = request.GET.get((name + '_' if name else '') + 'page')
    if page and page.isdigit():
        return int(page)
    else:
        return 1


@csrf_protect
@web_view(title=StringStorage.REGISTER.value, template_name='register')
def register_view(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        if not register_form.is_valid():
            register_form.add_error(None, StringStorage.FORM_FILLED_INCORRECTLY.value)
            return {'register_form': register_form}

        password = register_form.cleaned_data['password']
        repeat_password = register_form.cleaned_data['repeat_password']
        if password != repeat_password:
            register_form.add_error('password', StringStorage.PASSWORD_MISMATCH.value)
            return {'register_form': register_form}

        username = register_form.cleaned_data['username']
        if User.objects.filter(username=username):
            register_form.add_error('username', StringStorage.USERNAME_ALREADY_TAKEN.value)
            return {'register_form': register_form}

        user = User.objects.create_user(username=username.lower(),
                                        password=password,
                                        first_name=register_form.cleaned_data['first_name'],
                                        last_name=register_form.cleaned_data['last_name'])

        Student.objects.create(user_id=user.id,
                               group_id=register_form.cleaned_data['student_group'].id,
                               level_id=Level.objects.get(value=1).id,
                               rank_id=Rank.objects.get(code=RankCode.ORDINARY.value).id)

        personal_information = PersonalInformation.objects.get(user_id=user.id)
        personal_information.birthday = register_form.cleaned_data['birthday']
        personal_information.save()

        if request.user.is_authenticated:
            django_logout(request)

        django_login(request, user)
        return redirect('home')

    return {'register_form': RegisterForm()}


@csrf_protect
@web_view(title=StringStorage.LOGIN.value, template_name='login')
def login_view(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        if not login_form.is_valid():
            login_form.add_error(None, StringStorage.FORM_FILLED_INCORRECTLY.value)
            return {'login_form': login_form}
        user = authenticate(request,
                            username=login_form.cleaned_data['username'],
                            password=login_form.cleaned_data['password'])
        if not user:
            login_form.add_error(None, StringStorage.INVALID_USERNAME_AND_OR_PASSWORD.value)
            return {'login_form': login_form}

        if request.user.is_authenticated:
            django_logout(request)

        django_login(request, user)
        return redirect('home')

    return {'login_form': LoginForm()}


@csrf_exempt
def logout_view(request):
    django_logout(request)
    return redirect('login')


@web_view(title=NavigationItemTitle.USER.value, template_name='user')
def user_view(request, username: str):
    user: User = get_model_or_none(User, username=username)
    if not user:
        raise PageNotFoundException(request.path)

    return {
        'title': user.first_name + ' ' + user.last_name,
        'user': get_user(user=user),
    }


@csrf_protect
@web_view(title=NavigationItemTitle.HOME.value, template_name='home')
def home_view(request):
    filter_form = HomeFilterForm(request.GET)
    response = {
        'filter_form': filter_form,
    }

    if request.method == 'GET':
        if filter_form.is_valid():
            student = get_model_or_none(Student, user_id=request.user.id)
            teacher = get_model_or_none(Teacher, user_id=request.user.id)

            if student and not teacher and not request.user.is_staff:
                student_group_id = student.group.id
                only_current = True
            else:
                student_group = filter_form.cleaned_data['student_group']
                student_group_id = student_group.id if student_group else None
                only_current = filter_form.cleaned_data['only_current']

            response['events'] = get_event_list(student_group_id=student_group_id,
                                                is_current=only_current)

            response['tests'] = get_test_list(student_group_id=student_group_id,
                                              student_id=student.id if student else None,
                                              is_current=only_current)

            response['tasks_by_sections'] = get_task_list_by_sections(student_group_id=student_group_id,
                                                                      student_id=student.id if student else None,
                                                                      is_current=only_current)

            response['posts'] = get_post_list(student_group_id=student_group_id,
                                              user_id=request.user.id)

    return response


@csrf_protect
@web_view(title=NavigationItemTitle.RATING.value, template_name='rating')
def rating_view(request):
    if request.method == 'GET':
        rating_form = RatingFilterForm(request.GET)

        if rating_form.is_valid():
            student_group = rating_form.cleaned_data['student_group']
            date_begin = rating_form.cleaned_data['date_begin']
            date_end = rating_form.cleaned_data['date_end']
            sort_by_points_change = rating_form.cleaned_data['sort_by_points_change']

            updated_data = {}

            if not request.user.is_staff:
                student = get_model_or_none(Student, user_id=request.user.id)
                if student:
                    student_group = student.group
                    updated_data['student_group'] = student_group.id

            if not date_begin:
                date_begin = subtract_datetime(datetime_now(), days=7).date()
                updated_data['date_begin'] = date_begin

            if updated_data:
                update_form_data(rating_form, data=updated_data)

            data = get_student_rating_list(student_group_id=student_group.id if student_group else None,
                                           date_begin=date_begin,
                                           date_end=date_end,
                                           sort_by_points_change=sort_by_points_change)

            system = get_system()
            hide_rating = (system.hide_rating and not request.user.is_staff) if system else False
            if hide_rating:
                data = sorted(data, key=lambda x: x.student.user.last_name)

            rating_students = []
            for i, el in enumerate(data):
                image = PersonalInformation.objects.get(user_id=el.student.user.id).image
                item = {
                    'id': el.student.user.id,
                    'username': el.student.user.username,
                    'full_name': el.student.user.first_name + ' ' + el.student.user.last_name,
                    'image_url': image.url if image else None,
                    'student': {
                        'level': el.student.level.value,
                    },
                }
                if not hide_rating:
                    item['student']['points'] = el.points
                    item['student']['change_of_position'] = el.change_of_position
                    item['student']['change_of_points'] = el.change_of_position

                rating_students.append(item)

            return {
                'rating_students': rating_students,
                'rating_form': rating_form,
            }


@web_view(title=NavigationItemTitle.TASKS.value, template_name='tasks')
def tasks_view(request):
    return None


@web_view(title=NavigationItemTitle.ACHIEVEMENTS.value, template_name='achievements')
def achievements_view(request):
    student = get_model_or_none(Student, user_id=request.user.id)
    achievements = get_achievement_list(student_id=student.id if student else None,
                                        is_private=False)

    if student:
        # Отметим все полученные достижения как просмотренные
        student_achievement_list = StudentAchievement.objects.filter(student_id=student.id)
        for x in student_achievement_list:
            x.viewed = True
            x.save()

    return {
        'achievements': achievements,
    }


@web_view(title=NavigationItemTitle.ROADMAP.value, template_name='roadmap')
def roadmap_view(request):
    return None


@web_view(title=NavigationItemTitle.LINKS.value, template_name='links')
def links_view(request):
    link_groups = [{'name': x.name, 'links': []} for x in LinkGroup.objects.all().order_by('position')]
    links_raw = Link.objects.all().order_by('position')

    for link in links_raw:
        for i, group in enumerate(link_groups):
            if link.group.name == group['name']:
                link_groups[i]['id'] = link.group.id
                link_groups[i]['links'].append({
                    'id': link.id,
                    'name': link.name,
                    'url': link.url,
                    'description': link.description,
                })
                break

    return {
        'link_groups': link_groups,
    }


@csrf_protect
@web_view(title=NavigationItemTitle.FEEDBACK.value, template_name='feedback')
def feedback_view(request):
    page = get_page_number(request)
    feedback_form = FeedbackForm(request.POST)
    response = {
        'page': page,
        'feedback_form': feedback_form,
    }

    def _read_feedbacks():
        if not request.user.is_staff:
            return

        for key in request.POST:
            if key == 'read':
                value = request.POST[key]

                if value == 'all':
                    for feedback in Feedback.objects.filter(is_read=False):
                        feedback.is_read = True
                        feedback.save()

                elif value.isdigit():
                    feedback = Feedback.objects.get(id=int(value))
                    feedback.is_read = True
                    feedback.save()
                return

    def _proc_feedback_form():
        if 'send' not in request.POST:
            return

        if not feedback_form.is_valid():
            feedback_form.add_error(None, StringStorage.FORM_FILLED_INCORRECTLY.value)
            return response

        student = get_model_or_none(Student, user_id=request.user.id)
        Feedback.objects.create(text=feedback_form.cleaned_data['text'],
                                student_group_id=student.group.id if student else None)

        response['feedback_left'] = True
        response['feedback_form'] = FeedbackForm()

    def _get_feedbacks():
        feedbacks = Feedback.objects.all().order_by('is_read', '-datetime_create')
        paginator = Paginator(feedbacks, PAGE_LIMIT_DEFAULT)
        response['feedbacks'] = paginator.get_page(page)

    if request.method == 'POST':
        _read_feedbacks()
        _proc_feedback_form()
        _get_feedbacks()

    if request.user.is_staff and request.method == 'GET':
        _get_feedbacks()

    return response


@web_view(title=NavigationItemTitle.CONTROL.value, template_name='control')
def control_view(request):
    if not request.user.is_staff:
        raise PermissionDeniedException()

    return None


@web_view(title=StringStorage.NOTICES.value, template_name='notices')
def notices_view(request):
    if request.method == 'POST':
        read = request.POST.get('read')
        if read:
            mark_notices_as_read(user_id=request.user.id,
                                 notice_id=int(read) if read.isdigit() else None)
        elif read == 'all':
            mark_notices_as_read(user_id=request.user.id)

    page = get_page_number(request)
    return {
        'notices': get_notice_list(user_id=request.user.id, page=page),
        'page': page,
    }


@web_view(title=StringStorage.USER_EDIT.value, template_name='edit-user')
def edit_user_view(request):
    edit_form = UserEditForm(request.POST, request.FILES)
    personal_information = PersonalInformation.objects.get(user_id=request.user.id)
    response = {
        'edit_form': edit_form,
    }

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('user', username=request.user.username)

        if not edit_form.is_valid():
            edit_form.add_error(None, StringStorage.FORM_FILLED_INCORRECTLY.value)
            return response

        saved = False

        username = edit_form.cleaned_data['username']
        if username and username != request.user.username:
            if User.objects.filter(username=username):
                edit_form.add_error('username', StringStorage.USERNAME_ALREADY_TAKEN.value)
                return response

            user = User.objects.get(id=request.user.id)
            user.username = username
            user.save()
            saved = True

        for key in ('image', 'cover_image', 'birthday', 'about_me'):
            value = edit_form.cleaned_data.get(key)
            if value and value != getattr(personal_information, key):
                setattr(personal_information, key, value)
                saved = True

        if saved:
            personal_information.save()
            response['saved'] = True

    else:
        updated_data = {
            'username': personal_information.user.username,
        }
        for key in ('birthday', 'about_me'):
            value = getattr(personal_information, key)
            if value:
                updated_data[key] = value

        update_form_data(edit_form, data=updated_data)

    return response


@web_view(title=StringStorage.PROJECT.value, template_name='project')
def project_view(request, project_id: int):
    project: Project = get_model_or_none(Project, id=project_id)
    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    def _validate_permission():
        if not project:
            raise PageNotFoundException(request.path)

        if student:
            if project.student.user.id != request.user.id and not request.user.is_staff:
                raise PermissionDeniedException()

        elif not request.user.is_staff and not teacher:
            raise PermissionDeniedException()

    _validate_permission()

    response = {}
    comments_page = get_page_number(request, 'comments')
    project_ = get_project(project=project, comments_page=comments_page)

    # Если это проект пользователя, который сделал запрос
    if project.student.user.id == request.user.id:
        project_form = ProjectForm(request.POST)

        if request.method == 'POST':
            if 'cancel' in request.POST:
                return redirect('user', username=request.user.username)

            if not project_form.is_valid():
                project_form.add_error(None, StringStorage.FORM_FILLED_INCORRECTLY.value)
                return response

            saved = False
            for key in ('name', 'document_url', 'drawio_url', 'figma_url', 'github_url'):
                value = project_form.cleaned_data[key]
                if value and value != getattr(project, key):
                    setattr(project, key, value)
                    saved = True
            if saved:
                project.save()
                project_['status_code'] = project.status.code
                response['saved'] = True

        else:
            updated_data = {}
            for key in ('name', 'document_url', 'drawio_url', 'figma_url', 'github_url'):
                value = getattr(project, key)
                if value:
                    updated_data[key] = value
            update_form_data(project_form, data=updated_data)

        response['project_form'] = project_form

    response['project'] = project_
    return response


@web_view(title=StringStorage.POST.value, template_name='post')
def post_view(request, post_id: int):
    post: Post = get_model_or_none(Post, id=post_id)
    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    post_for_student_group = (get_first_model_or_none(PostForStudentGroup,
                                                      post_id=post.id,
                                                      student_group_id=student.group.id)
                              if student else None)

    def _validate_permission():
        if not post:
            raise PageNotFoundException(request.path)

        if student:
            if not post_for_student_group and not request.user.is_staff:
                raise PermissionDeniedException()

        elif not request.user.is_staff and not teacher:
            raise PermissionDeniedException()

    _validate_permission()

    next_post = get_model_or_none(Post, id=post.id + 1)
    prev_post = get_model_or_none(Post, id=post.id - 1) if post.id > 1 else None

    if PostView.objects.get_or_create(post_id=post.id, user_id=request.user.id)[1]:
        post.count_views += 1

    comments_page = get_page_number(request, 'comments')
    return {
        'title': post.header,
        'post': get_post(post=post, comments_page=comments_page),
        'next_post_id': next_post.id if next_post else None,
        'prev_post_id': prev_post.id if prev_post else None,
    }


@web_view(title=StringStorage.EVENT.value, template_name='event')
def event_view(request, event_id: int):
    event: Event = get_model_or_none(Event, id=event_id)
    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    assigned_event = (get_first_model_or_none(AssignedEvent,
                                              event_id=event_id,
                                              student_group_id=student.group.id)
                      if student else None)

    def _validate_permission():
        if not event:
            raise PageNotFoundException(path=request.path)

        if student:
            if not assigned_event and not request.user.is_staff:
                raise PermissionDeniedException()

        elif not request.user.is_staff and not teacher:
            raise PermissionDeniedException()

    _validate_permission()

    response = {
        'event': get_event(event=event, assigned_event=assigned_event),
    }
    if request.user.is_staff and teacher:
        response['events_assigned_by_groups'] = get_events_assigned_by_groups(event_id=event_id)

    return response


@web_view(title=StringStorage.TEST.value, template_name='test')
def test_view(request, test_id: int):
    test = get_model_or_none(Test, id=test_id)
    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    assigned_test = (get_first_model_or_none(AssignedTest,
                                             test_id=test_id,
                                             student_group_id=student.group.id)
                     if student else None)

    def _validate_permission():
        if not test:
            raise PageNotFoundException(path=request.path)

        if student:
            if not assigned_test and not request.user.is_staff:
                raise PermissionDeniedException()

        elif not request.user.is_staff and not teacher:
            raise PermissionDeniedException()

    _validate_permission()

    response = {
        'test': get_test(test=test, assigned_test=assigned_test),
    }
    return response


@web_view(title=StringStorage.TASK.value, template_name='task')
def task_view(request, task_id: int):
    task = get_model_or_none(Task, id=task_id)
    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    assigned_task: AssignedTask = (get_first_model_or_none(AssignedTask,
                                                           task_id=task_id,
                                                           student_group_id=student.group.id)
                                   if student else None)

    completing_task: CompletingTask = (get_first_model_or_none(CompletingTask,
                                                               assigned_task_id=assigned_task.id,
                                                               student_id=student.id)
                                       if assigned_task else None)

    def _validate_permission():
        if not task:
            raise PageNotFoundException(path=request.path)

        if student:
            if not assigned_task and not request.user.is_staff:
                raise PermissionDeniedException()

            if not request.user.is_staff:
                dt_now = datetime_now()
                if assigned_task.readline and not assigned_task.deadline and assigned_task.readline < dt_now:
                    raise PermissionDeniedException()

                if assigned_task.deadline and assigned_task.deadline < dt_now:
                    raise PermissionDeniedException()

        elif not request.user.is_staff and not teacher:
            raise PermissionDeniedException()

    _validate_permission()

    response = {}
    if assigned_task:
        if not completing_task:
            completing_task = CompletingTask.objects.create(student_id=student.id,
                                                            assigned_task_id=assigned_task.id,
                                                            status_id=TaskStatus.objects.get(
                                                                code=TaskStatusCode.ASSIGNED.value).id)

        if request.method == 'POST':
            if 'cancel' in request.POST:
                completing_task.status_id = TaskStatus.objects.get(code=TaskStatusCode.ASSIGNED.value).id
                completing_task.kwargs['check'] = False

            else:
                answer_format_code = completing_task.assigned_task.task.answer_format.code

                if answer_format_code == AnswerFormatCode.TEXT.value:
                    completing_task.kwargs = {
                        'text': request.POST.get('text'),
                    }

                elif answer_format_code == AnswerFormatCode.PROGRAM_TEXT.value:
                    files = []
                    i = 1
                    while True:
                        file_name = request.POST.get('file_name_' + str(i))
                        file_text = request.POST.get('file_text_' + str(i))
                        if not file_name or not file_text:
                            break

                        files.append({
                            'name': file_name,
                            'text': file_text,
                        })
                        i += 1

                    completing_task.kwargs = {
                        'files': files,
                    }

                completing_task.kwargs['check'] = True

            completing_task.save()
            return redirect('task', task_id=task_id)

    comments_page = get_page_number(request, 'comments')
    private_comments_page = get_page_number(request, 'private_comments')
    response['task'] = get_task(task=task,
                                assigned_task=assigned_task,
                                completing_task=completing_task,
                                comments_page=comments_page,
                                private_comments_page=private_comments_page)

    return response


@web_view(title=StringStorage.PAGE_NOT_FOUND.value, template_name='not_found')
def page_not_found_view(request, exception):
    raise PageNotFoundException(path=request.path)
