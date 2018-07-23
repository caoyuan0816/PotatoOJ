from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group


__all__ = ['PotatoPlant', 'Question', 'Mission',
           'Contest', 'ContestPubQuestions', 'GroupProfile',
           'ContestMission']


class PotatoPlant(models.Model):
    """
    The extension of django.contrib.auth.models.User.
    Will save potatooj's user data into this model.
    It is a onetoone relationship with default User model.
    Fields:
        - signature: Every user has a signature, user can edit it by themself
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signature = models.CharField('signature', max_length=100)


class Question(models.Model):
    """
    The Quesiton model is used to stroe information and limitation of questions.
    There are several informations we should pay attention to:
        - id: primary key, automatically created by django.
        - title: the title of quesion.
        - source: the author or website who created the problem.
        - description: the description of questoin. Format: ***Markdown***
        - description_input: the description of input values.
        - description_output: the description of ouput values.
        - sample_input: the input samples. Format: ***Markdown***
        - sample_output: the output samples. Format: ***Markdown***
        - hint: some question have hint.
        - time_limit: limitation of time, unit: ms.
        - memory_limit: limitation of memory using. unit: kb.
        - is_special_judge: need or not need special judge.
        - submit_num: the total submition number of this question.
        - ac_num: the total accepted number of this question.
        - add_date: first public date of this question.
        - modify_date: last modify date of this question.
    """
    title = models.CharField('title', max_length=100)
    source = models.CharField('source', max_length=100)
    description = models.TextField('description, format: markdown')
    description_input = models.TextField('description of input, format: markdown')
    description_output = models.TextField('description of output, format: markdown')
    sample_input = models.TextField('sample input, format: markdown')
    sample_output = models.TextField('sample output, format: markdown')
    hint = models.TextField('some question have hints', blank=True)
    time_limit = models.PositiveIntegerField('time limit, unit: ms')
    memory_limit = models.PositiveIntegerField('memory limit, unit: kb')
    is_special_judge = models.BooleanField('need or not need special judge, boolean')
    submit_num = models.PositiveIntegerField('total submition number.')
    ac_num = models.PositiveIntegerField('total accepted number.')
    add_date = models.DateTimeField('first public date', auto_now_add=True)
    modify_date = models.DateTimeField('last modified date', auto_now=True)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.title

    def get_answer_path(self):
        """
        Return the storage path of question's standard answer.
        It is decided by MEDIA_ROOT setting value.
        Should use this method after saved model into databases.
        """
        return "{}/question/{}".format(
            settings.MEDIA_ROOT,
            self.id)


class Mission(models.Model):
    """
    The Mission model used to store missions.
    When users submit code, the submission will become a mission store into database.
    The judging system will automatically judge the mission and update the status code of mission.
    Fields:
        - id: mission id, primary key.
        - user: the user who submit the mission, foreign key of User.id.
        - question: corresponding question, foreign key of Question.id.
        - lang_code:
            - 0: c
            - 1: cpp
            - 2: cpp11
            - 3: java
            - 4: py2
            - 5: py3
        - status_code:
            - 0: pending
            - 1: judging
            - 2: Accepted
            - 3: PresentationError
            - 4: WrongAnswer
            - 5: TimeLimitExceeded
            - 6: MemoryLimitExceeded
            - 7: OutputLimitExceeded
            - 8: RuntimeError
            - 9: CompilationError
        - submit_time: the time when user submit mission.
        - judge_time: the time when judging system has already judged and updated this mission.
        - judge_info: show the details of some kind of error status.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField('code content')
    language = models.CharField('language code', max_length=30)
    status = models.CharField('status code', max_length=100)
    submit_time = models.DateTimeField('first public dat', auto_now_add=True)
    judge_time = models.DateTimeField('last modified date', auto_now=True)
    judge_info = models.TextField('details of judging result', blank=True)

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"

    def __str__(self):
        return "Mission id: {}".format(self.id)


class Contest(models.Model):
    """
    Contest is a collection of question, and every contest have a begin time and end time.
    Each contest have a owner who create the contest.
    Contest can be public or private, owner can change settings of contest.
    Fields:
        - id: primary key, automatically created by django.
        - creater: the user who create contest, foreign key of User.id.
        - questions: the questions which belong to this contest.
        - title: name of contest, can modify by creater.
        - notification: additional information provided to users.
        - create_time: the time contest created.
        - start_time: the time when contest start.
        - finish_time: the time when contest finish.
        - is_public: is or not a public contest.
        - password: if the contest is private, save the password of contest, can change by creater.
    """
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_questions = models.ManyToManyField(Question, through='ContestPubQuestions')
    title = models.CharField('title', max_length=100)
    notification = models.TextField('notification', blank=True)
    create_time = models.DateTimeField('first public dat', auto_now_add=True)
    start_time = models.DateTimeField('start time of contest')
    finish_time = models.DateTimeField('end time of contest')
    is_public = models.BooleanField('is or not public contest')
    password = models.CharField('password of contest',max_length=20, blank=True)

    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"
        permissions = (
            ('view_contest', 'View contest'),
        )

    def __str__(self):
        return "contest id: {}, title: {}".format(
            self.id,
            self.title)


class ContestMission(models.Model):
    """
    Same as model Mission, but used to contest.
    Add field:
        - contest id.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField('code content')
    language = models.CharField('language code', max_length=30)
    status = models.CharField('status code', max_length=100)
    submit_time = models.DateTimeField('first public dat', auto_now_add=True)
    judge_time = models.DateTimeField('last modified date', auto_now=True)
    judge_info = models.TextField('details of judging result', blank=True)
    contest =  models.ForeignKey(Contest, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "ContestMission"
        verbose_name_plural = "ContestMissions"

    def __str__(self):
        return "Contest Mission id: {}".format(self.id)


class ContestPubQuestions(models.Model):
    """
    Contest using this model as a through class.
    Will save some extra information about contest and questions.
    """
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    question_serial_letter = models.CharField('serial letter. Example: A, B, C', max_length=5)


class GroupProfile(models.Model):
    """
    Profile of Group
    Fields:
        - creator   Creator of Group
        - manager   Manager of Group, capable of adding, removing user
        - create_time   Create date time of Group
        - description   Description of Group
        - notification  Notification for group users
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='profile')
    creator = models.ForeignKey(User, verbose_name="group creator", related_name='creator')
    manager = models.ForeignKey(User, verbose_name="group manager", related_name='manager')
    create_time = models.DateTimeField('create time of group', auto_now_add=True)
    description = models.TextField('group description', blank=True)
    notification = models.TextField('notification', blank=True)
