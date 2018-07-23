import urllib
import datetime
import math

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from potato.models import *
from potato.serializers import *
from rest_framework import status
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign_perm
from .decorators import action_response, require_permission
from .tasks import judge


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def whoami(request):
    """
    Tell me who am I.
    If user already logged in, will return user name.
    Else will return anonymous user.
    """
    content = {
        'success': True,
        'user': 'AnonymousUser'
    }
    if not request.user.id is None:
        content['user'] = str(request.user)
        content['id'] = request.user.id
    return Response(content)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def api_login(request):
    """
    API Login.
    Only accept POST method.
    Form data should include username, password and csrfmiddlewaretoken.
    """
    content = {
        'success': False,
    }
    # Check params
    try:
        username = request.data['username']
        password = request.data['password']
    except KeyError as e:
        content['detail'] = str(e)
        return Response(content)

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            content['success'] = True
        else:
            content['detail'] = 'Sorry, this user is disabled. Please contact admin.'
    else:
        content['detail'] = 'Invalid login'
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_logout(request):
    """
    API logout.
    Using GET method access this API and user will log out from website.
    """
    content = {
        'success': True
    }
    logout(request)
    return Response(content)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def api_register(request):
    """
    API register.
    Using POST method to register a new user.
    """
    content = {
        'success': False,
    }
    # Check POST arguments
    try:
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']
    except KeyError as e:
        content['detail'] = str(e)
        return Response(content)
    # Create user
    try:
        new_user = User.objects.create_user(\
            username=username,
            email=email,
            password=password)
        new_user.save()
        new_potato_plant = PotatoPlant(\
            user=new_user,
            signature='')
        new_potato_plant.save()
    except Exception:
        content['detail'] = 'please change a username or email address.'
        return Response(content)

    content['success'] = True
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_questions(request):
    """
    List all quesionts.
    """
    content = {
        'success': False,
    }
    try:
        questions = Question.objects.all().order_by('id')
        serializer = QuestionListSerializer(questions, many=True)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    # Add additional informations
    if request.user.is_authenticated():
        missions = Mission.objects.filter(user_id__exact=request.user.id)
        content['ac_list'] = [mission.question_id for mission in missions\
                                .filter(status__exact=4).distinct('question_id')\
                                .order_by('question_id')]

    content['questions'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_question_details(request, pid):
    """
    API problem details.
    Return detailed information of single problem.
    Example: /api/question/1/
    """
    content = {
        'success': False
    }

    try:
        question = Question.objects.get(id=pid)
        serializer = QuestionSerializer(question)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    content['question'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_submit(request):
    """
    API submit.
    Submit a question to celery task queue.
    Workers will auto judge and store the result to database.
    When the task is running, the state infomation will sotre into redis.
    """
    content = {
        'success': False
    }
    try:
        code = request.data['code']
        code = urllib.parse.unquote(code)
        language = request.data['language']
        qid = request.data['question']
        try:
            contest = request.data['contest']
            is_contest = True
        except KeyError as e:
            is_contest = False
    except KeyError as e:
        content['detail'] = str(e)
        return Response(content)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    try:
        question = Question.objects.get(id=qid)
        time_limit = question.time_limit
        memory_limit = question.memory_limit
        is_special_judge = question.is_special_judge
        
        if not is_contest:
            new_mission = Mission(user=request.user,
                                  question=question,
                                  code=code,
                                  language=language,
                                  status=0,
                                  judge_info='')
            new_mission.save()
        else:
            contest_instance = Contest.objects.get(id=contest)
            # Check contest was or not finished
            if contest_instance.finish_time < datetime.datetime.now(datetime.timezone.utc):
                # Finished
                content['detail'] = 'Contest is finished.'
                return Response(content)
            new_mission = ContestMission(user=request.user,
                                  question=question,
                                  code=code,
                                  language=language,
                                  status=0,
                                  contest=contest_instance,
                                  judge_info='')
            new_mission.save()
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    try:
        result = judge.delay(run_id=new_mission.id,
                             code=code,
                             language=language,
                             max_time=time_limit,
                             max_memory=memory_limit,
                             # data_dir=data_dir,
                             data_id=qid,
                             is_contest=is_contest,
                             special_judge=is_special_judge)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    content['success'] = True
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_statuses(request):
    """
    API statuses.
    Will return the list of all statuses.
    """
    content = {
        'success': False,
    }
    try:
        missions = Mission.objects.all().order_by('id').reverse()
        serializer = MissionListSerializer(missions, many=True)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    content['statuses'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_contests(request):
    """
    API contests.
    Will return the list of all contests.
    """
    content = {
        'success': False
    }
    try:
        contests = Contest.objects.all().order_by('id').reverse()
        serializer = ContestListSerializer(contests
            , many=True)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    content['contests'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_contest_details(request, cid):
    """
    API contest details.
    Will return all details of a contest.
    """
    content = {
        'success': False
    }
    try:
        contest = Contest.objects.get(id=cid)
        serializer = ContestSerializer(contest)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)

    content['contest'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_user_details(request, uid):
    """
    API user details.
    Will return user information and user's statistic information.
    """
    content = {
        'success': False,
        'is_me': False
    }
     
    try:
        user = User.objects.get(id=uid)
        serializer = UserDetailsSerializer(user)
        content['userdetails'] = serializer.data
        missions = Mission.objects.filter(user_id__exact=uid)
        content['userdetails']['profile']['ac_list'] = \
            [mission.question_id for mission in missions\
                .filter(status__exact=4)\
                .distinct('question_id').order_by('question_id')]
        content['userdetails']['profile']['try_list'] = \
        list(set([mission.question_id for mission in missions\
                .exclude(status__exact=4)\
                .distinct('question_id').order_by('question_id')])\
             - set(content['userdetails']['profile']['ac_list']))
        content['userdetails']['profile']['submitions'] = \
            [missions.filter(status__exact=x)\
                .count() for x in range(4, 13)]
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    # Check user is or not himself
    if str(request.user) != 'AnonymousUser' and int(request.user.id) == int(uid):
        content['is_me']= True
    content['success'] = True
    return Response(content)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_status_details(request, sid):
    content = {
        'success': False
    }
    try:
        status = Mission.objects.get(id=sid)
        if int(status.user.id) != request.user.id:
            content['detail'] = 'You can only read your own code!'
            return Response(content)
        serializer = MissionDetailsSerializer(status)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    content['status'] = serializer.data
    content['success'] = True
    return Response(content)


class APIGroupList(APIView):
    """
    API group: get group list, create group
    Use view class name style in http://www.django-rest-framework.org/tutorial/3-class-based-views/
    """
    @authentication_classes((SessionAuthentication,))
    @permission_classes((IsAuthenticated,))
    @action_response
    def post(self, request):
        name = request.data['name']
        description = request.data['description']
        user = request.user
        grp = Group.objects.create(name=name)
        GroupProfile.objects.create(group=grp, creator=user, manager=user, description=description)
        user.groups.add(grp)
        return grp.id

    def get(self):
        pass


class APIGroupDetail(APIView):
    """
        API group: get group detail, change field
        Use view class name style in http://www.django-rest-framework.org/tutorial/3-class-based-views/
    """
    @authentication_classes((SessionAuthentication,))
    @permission_classes((IsAuthenticated,))
    @action_response
    def get(self, request, group_id):
        if not request.user.groups.filter(id=int(group_id)).exists():
            raise Exception('Not in the group')
        grp = Group.objects.get(id=int(group_id))
        return GroupSerializer(grp).data

    def put(self):
        pass


class APIGroupUserList(APIView):
    """
        API Group User: add user to group, get user list of group
        Use view class name style in http://www.django-rest-framework.org/tutorial/3-class-based-views/
    """
    @authentication_classes((SessionAuthentication,))
    @permission_classes((IsAuthenticated,))
    @action_response
    def post(self, request, group_id):
        grp = Group.objects.get(id=int(group_id))
        if grp.profile.manager != request.user:
            raise Exception('Not manager of group')
        user_id = int(request.data['user_id'])
        user = User.objects.get(id=user_id)
        user.groups.add(grp)

    def get(self):
        pass


class APIGroupUserDetail(APIView):
    """
        API Group User Detail: delete user from group
        Use view class name style in http://www.django-rest-framework.org/tutorial/3-class-based-views/
    """
    @authentication_classes((SessionAuthentication,))
    @permission_classes((IsAuthenticated,))
    @action_response
    def delete(self, request, group_id, user_id):
        grp = Group.objects.get(id=int(group_id))
        if grp.profile.manager != request.user:
            raise Exception('Not manager of group')
        user = User.objects.get(id=int(user_id))
        user.groups.remove(grp)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@require_permission('view_contest', (Contest, 'id', 'contest_id'))
def api_test_permission(request, contest_id):
    """
        Test api for require object permission
    """
    return Response('{} success'.format(contest_id))


@api_view(['post'])
@authentication_classes((SessionAuthentication, ))
@action_response
def api_test_assign_permission(request):
    """
        Test api for assign object permission
    """
    user_id = int(request.data['user_id'])
    contest_id = int(request.data['contest_id'])
    user = User.objects.get(id=user_id)
    contest = Contest.objects.get(id=contest_id)
    assign_perm('view_contest', user, contest)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((AllowAny, ))
def api_problem_status(request, pid):
    """
    API problem status.
    Show statistic data of a single problem.
    """
    content = {
        'success': False,
        'question': {}
    }
    try:
        question = Question.objects.get(id=pid)
        content['question']['id'] = pid
        content['question']['title'] = question.title
        missions = Mission.objects.filter(question_id__exact=pid)
        base = datetime.date.today()
        date_list = [base - datetime.timedelta(days=x) for x in range(0, 10)][::-1]
        content['question']['language_list'] = \
            [missions.filter(language__exact=x)\
                .count() for x in range(0, 5)]
        content['question']['status_list'] = \
            [missions.filter(status__exact=x)\
                .count() for x in range(4, 13)]
        content['question']['attention_days'] = date_list
        content['question']['attention_values'] = \
            [missions.filter(submit_time__year=x.year,
                            submit_time__month=x.month,
                            submit_time__day=x.day)\
                     .count() for x in date_list]

    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    content['success'] = True
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_contest_rank_list(request, cid):
    content = {
        'success': False,
        'contest_rank': {}
    }
    try:
        contest = Contest.objects.get(id=cid)
        contest_problem_len = contest.pub_questions.count()
        cotest_serializer = ContestListSerializer(contest)
        contest_start_time = contest.start_time
        question_letter_list = ContestPubQuestions.objects\
                               .filter(contest_id__exact=cid)\
                               .order_by('question_serial_letter')\
                               .values_list('question_id', 'question_serial_letter')
        question_letter_dict = {}
        for x in question_letter_list:
            question_letter_dict[x[1]] = x[0]
        question_letter_dict_reverse = {}
        for x in question_letter_list:
            question_letter_dict_reverse[x[0]] = x[1]
        # List used to record FB
        question_first_ac_dict = {}
        for x in question_letter_list:
            question_first_ac_dict[x[0]] = False
        question_letter_list = list(map(lambda x:x[1], question_letter_list))
       
        status_list = [str(x) for x in range(4, 13)]
        missions_list = list(map(
                lambda x:[x[0], x[1], int(x[2]),
                    math.floor((x[3] - contest_start_time).total_seconds())],
                ContestMission.objects\
                    .filter(contest_id__exact=cid)\
                    .filter(status__in=status_list)\
                    .order_by('id')\
                    .values_list('question_id',
                                 'user_id',
                                 'status',
                                 'submit_time')))
        user_list = list(map(lambda x:[x[0], x[1]],
                        ContestMission.objects\
                        .filter(contest_id__exact=cid)\
                        .filter(status__in=status_list)\
                        .values_list('user_id', 'user__username')\
                        .annotate(Count('user_id', 'user__username'))))
        rank_data = []
        for user in user_list:
            rank_data.append({
                'id': str(user[0]),
                'username': user[1],
                'total_time': 0,
                'solved': 0
            })
        user_list = list(map(lambda x:x[0], user_list))

        def _calculate_rank(user_mission, i, user):
            problem = user_mission[0]
            # Check key value
            if str(problem) not in rank_data[i]:
                rank_data[i][str(problem)] = {
                    'punish': 0,
                    'time': 0,
                    'ac': False,
                    'fb': False
                }
            # If already AC, pass
            if rank_data[i][str(problem)]['ac']:
                return
            # Check AC
            if user_mission[2] == 4:
                rank_data[i][str(problem)]['ac'] = True
                rank_data[i][str(problem)]['time'] =\
                    (rank_data[i][str(problem)]['punish'] * 20) +\
                        (user_mission[3] // 60)
                rank_data[i]['total_time'] +=\
                    rank_data[i][str(problem)]['time']
                rank_data[i]['solved'] += 1
                # Check FB
                if not question_first_ac_dict[problem]:
                    question_first_ac_dict[problem] = True
                    rank_data[i][str(problem)]['fb'] = True
            else:
                rank_data[i][str(problem)]['punish'] += 1

        for i, user in enumerate(user_list):
            for user_mission in filter(lambda mission:mission[1]==user, missions_list):
                _calculate_rank(user_mission, i, user)

        non_zero_rank_list = []
        zero_rank_list = []
        # Sort rank
        for rank in rank_data:
            if rank['total_time'] == 0:
                zero_rank_list.append(rank)
            else:
                non_zero_rank_list.append(rank)

        def _cmp_to_key():
            '''
                Convert a cmp= function into a key= function
            '''
            class K:
                def __init__(self, obj, *args):
                    self.obj = obj
                def __lt__(self, other):
                    if self.obj['solved'] > other.obj['solved']:
                        return True
                    elif self.obj['solved'] == other.obj['solved']:
                        if self.obj['total_time'] < other.obj['total_time']:
                            return True
                    return False
                def __gt__(self, other):
                    return not __lt__(self, other) and not __eq__(self, other)
                def __eq__(self, other):
                    if self.obj['solved'] == other.obj['solved'] and \
                        self.obj['total_time'] == other.obj['total_time']:
                        return True
                    return False
                def __le__(self, other):
                    return not __gt__(self, other)
                def __ge__(self, other):
                    return not __lt__(self, other)
                def __ne__(self, other):
                    return not __eq__(self, other)
            return K
        non_zero_rank_list.sort(key=_cmp_to_key())

        rank_list = non_zero_rank_list + zero_rank_list

    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    content['contest_rank']['rank_list'] = rank_list
    content['contest_rank']['contest_details'] = cotest_serializer.data
    content['contest_rank']['question_letter_dict'] = question_letter_dict
    content['contest_rank']['question_letter_dict_reverse'] = question_letter_dict_reverse
    content['contest_rank']['question_letter_list'] = question_letter_list
    content['success'] = True
    return Response(content)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_contest_status_list(request, cid):
    """
    API contest status list.
    Will return information of contest misson.
    """
    content = {
        'success': False
    }
    try:
        contest_missions = ContestMission.objects\
                           .filter(contest_id__exact = cid)\
                           .order_by('submit_time')
        serializer = ContestMissionListSerializer(contest_missions, many=True)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    content['contest_status_list'] = serializer.data
    content['success'] = True
    return Response(content)


@api_view(['get'])
@authentication_classes((SessionAuthentication, ))
@permission_classes((IsAuthenticated, ))
def api_contest_status_details(request, cid, sid):
    content = {
        'success': False
    }
    try:
        question_letter_list = ContestPubQuestions.objects\
                               .filter(contest_id__exact=cid)\
                               .order_by('question_serial_letter')\
                               .values_list('question_id', 'question_serial_letter')
        question_letter_dict = {}
        for x in question_letter_list:
            question_letter_dict[x[1]] = x[0]
        question_letter_dict_reverse = {}
        for x in question_letter_list:
            question_letter_dict_reverse[x[0]] = x[1]

        contest_status = ContestMission.objects.get(id=sid)
        if int(contest_status.user.id) != request.user.id:
            content['detail'] = 'You can only read your own code!'
            return Response(content)
        serializer = ContestMissionDetailsSerializer(contest_status)
    except Exception as e:
        content['detail'] = str(e)
        return Response(content)
    content['status'] = serializer.data
    content['question_letter_dict'] = question_letter_dict
    content['question_letter_dict_reverse'] = question_letter_dict_reverse
    content['success'] = True
    return Response(content)
