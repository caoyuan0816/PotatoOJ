from rest_framework import serializers
from potato.models import *
from django.contrib.auth.models import User, Group


__all__ = ['QuestionSerializer', 'QuestionListSerializer', 'MissionListSerializer',
           'ContestSerializer', 'ContestListSerializer', 'ContestPubQuestionsSerializer',
           'GroupSerializer', 'UserDetailsSerializer', 'MissionDetailsSerializer',
           'ContestMissionListSerializer', 'ContestMissionDetailsSerializer']


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Serialization class of QuestionList.
    This class will return a array list of questions including:
        - id
        - title
        - source
        - submit_num
        - ac_num
    Only can used to show the question list, can not used to add any question.
    """
    class Meta:
        model = Question
        fields = ('id',
                  'title',
                  'source',
                  'submit_num',
                  'ac_num')


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serialization class of Question.
    Whill return details of single question:
        - id
        - title
        - source
        - description
        - description_input
        - description_output
        - sample_input
        - sample_output
        - hint
        - time_limit
        - memory_limit
        - is_special_judge
        - add_date
        - modify_date
    """
    class Meta:
        model = Question
        fields = ('id',
                  'title',
                  'source',
                  'description',
                  'description_input',
                  'description_output',
                  'sample_input',
                  'sample_output',
                  'hint',
                  'time_limit',
                  'memory_limit',
                  'is_special_judge',
                  'add_date',
                  'modify_date')


class MissionListSerializer(serializers.ModelSerializer):
    """
    Serialization class of MissionList.
    This class will return a array list of missions including:
        - id
        - user
        - question
        - language
        - status
        - submit_time
        - judge_time
        - judge_info
    Only can used to show the mission list, can not used to add any Mission.
    """
    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
            - id
            - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')

    class _QuestionSerializer(serializers.ModelSerializer):
        '''
        Will return details of single question:
            - id
            - title
        '''
        class Meta:
            model = Question
            fields = ('id',
                      'title')

    user_details = _UserSerializer(source='user')
    question_details = _QuestionSerializer(source='question')
    class Meta:
        model = Mission
        fields = ('id',
                  'user_details',
                  'question_details',
                  'language',
                  'status',
                  'submit_time',
                  'judge_time',
                  'judge_info')


class ContestListSerializer(serializers.ModelSerializer):
    """
    Serialization class of ContestListSerializerList.
    This class will return a array list of contests including:
        - id
        - creater_details
        - title
        - create_time
        - start_time
        - finish_time
        - is_public
    Only can used to show the contest list, can not used to add any contest.
    """
    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
          - id
          - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')
    creater_details = _UserSerializer(source='creater')
    class Meta:
        model = Contest
        fields = ('id',
                  'creater_details',
                  'title',
                  'create_time',
                  'start_time',
                  'finish_time',
                  'is_public')


class ContestSerializer(serializers.ModelSerializer):
    """
    Serialization class of Contest.
    Will return all details of a contest, indcluding:
        - id
        - creater_details
        - title
        - notification
        - create_time
        - start_time
        - finish_time
        - is_public
    """

    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
          - id
          - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')

    creater_details = _UserSerializer(source='creater')
    pub_questions_details = serializers.SerializerMethodField('get_pub_questions', read_only=True)

    def get_pub_questions(self, contest):
      qs = ContestPubQuestions.objects.filter(contest=contest).order_by('question_serial_letter')
      ser = ContestPubQuestionsSerializer(instance=qs, many=True)
      return ser.data

    class Meta:
        model = Contest
        fields = ('id',
                  'creater_details',
                  'pub_questions_details',
                  'title',
                  'notification',
                  'create_time',
                  'start_time',
                  'finish_time',
                  'is_public')


class ContestPubQuestionsSerializer(serializers.ModelSerializer):
    """
    Serializer of ContestPubQuestions model.
    It is a model which is used to store m2m relationship bettween Contest and Questions model.
    """
    question_detail = QuestionSerializer(source='question')
    class Meta:
        model = ContestPubQuestions
        fields = ('question_serial_letter',
                  'question_detail',)


class PotatoPlantSerializer(serializers.ModelSerializer):
        class Meta:
            model = PotatoPlant
            fields = ('signature',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    UserDetailsSerializer used to show user's information and statistic information.
    """
    profile = serializers.SerializerMethodField('get_potato_profile', read_only=True)

    def get_potato_profile(self, user):
        return PotatoPlantSerializer(instance=user.potatoplant).data

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'last_login',
                  'date_joined',
                  'is_staff',
                  'groups',
                  'profile')


class GroupSerializer(serializers.ModelSerializer):
    """
        Serialization class of Group.
        This class will detail of Group including:
            - id
            - name
            - creator
            - manager
            - create_time
            - description
            - notification
            - members
        """
    class _UserSerializer(serializers.ModelSerializer):
        """
        Return details of single user:
          - id
          - username
        """
        class Meta:
            model = User
            fields = ('id', 'username')

    creator = _UserSerializer(source='profile.creator')
    manager = _UserSerializer(source='profile.manager')
    create_time = serializers.DateTimeField(source='profile.create_time')
    description = serializers.CharField(source='profile.description')
    notification = serializers.CharField(source='profile.notification')

    def get_members(self, group):
        return [self._UserSerializer(user).data for user in group.user_set.all()]
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'creator', 'manager', 'create_time', 'description', 'notification', 'members')


class MissionDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer of Mission model.
    Will return all information about a single mission.
    """
    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
            - id
            - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')

    class _QuestionSerializer(serializers.ModelSerializer):
        '''
        Will return details of single question:
            - id
            - title
        '''
        class Meta:
            model = Question
            fields = ('id',
                      'title')

    user_details = _UserSerializer(source='user')
    question_details = _QuestionSerializer(source='question')
    class Meta:
        model = Mission
        fields = ('id',
                  'user_details',
                  'question_details',
                  'code',
                  'language',
                  'status',
                  'submit_time',
                  'judge_time',
                  'judge_info')


class ContestMissionListSerializer(serializers.ModelSerializer):
    """
    Serializer of Contest Mission model.
    Will return all missions.
    Fields:
        - id
        - user
        - question
        - language
        - status
        - submit_time
        - judge_time
        - judge_info
    Only can used to show the mission list, can not used to add any Mission.
    """
    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
            - id
            - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')

    class _QuestionSerializer(serializers.ModelSerializer):
        '''
        Will return details of single question:
            - id
            - title
        '''
        class Meta:
            model = Question
            fields = ('id',
                      'title')

    user_details = _UserSerializer(source='user')
    question_details = _QuestionSerializer(source='question')
    class Meta:
        model = ContestMission
        fields = ('id',
                  'user_details',
                  'question_details',
                  'language',
                  'status',
                  'submit_time',
                  'judge_time',
                  'judge_info')


class ContestMissionDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer of ContestMission model.
    Will return all information about a single mission.
    """
    class _UserSerializer(serializers.ModelSerializer):
        '''
        Will return details of single user:
            - id
            - username
        '''
        class Meta:
            model = User
            fields = ('id',
                      'username')

    class _QuestionSerializer(serializers.ModelSerializer):
        '''
        Will return details of single question:
            - id
            - title
        '''
        class Meta:
            model = Question
            fields = ('id',
                      'title')

    user_details = _UserSerializer(source='user')
    question_details = _QuestionSerializer(source='question')
    class Meta:
        model = ContestMission
        fields = ('id',
                  'user_details',
                  'question_details',
                  'code',
                  'language',
                  'status',
                  'submit_time',
                  'judge_time',
                  'judge_info')

